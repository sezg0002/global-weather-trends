import os
import pandas as pd
from sqlalchemy.orm import mapped_column, Session
from sqlalchemy import Integer, String, Float, DateTime, Date, Index, text
from models.base import Base, get_engine, get_session

DATA_DIR = os.getenv("DATA_DIR", "data")


# -------------------------
# Dimension Table
# -------------------------
class DimCity(Base):
    __tablename__ = "dim_city"

    city_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    city = mapped_column(String(128), nullable=False, unique=True)
    country = mapped_column(String(128), nullable=True)
    latitude = mapped_column(Float, nullable=False)
    longitude = mapped_column(Float, nullable=False)
    timezone = mapped_column(String(64), nullable=True)


# -------------------------
# Fact Table - Hourly
# -------------------------
class FactWeatherHourly(Base):
    __tablename__ = "fact_weather_hourly"

    city_id = mapped_column(Integer, primary_key=True)
    ts_utc = mapped_column(DateTime, primary_key=True)

    temperature_2m = mapped_column(Float, nullable=True)
    relative_humidity_2m = mapped_column(Float, nullable=True)
    apparent_temperature = mapped_column(Float, nullable=True)
    precipitation = mapped_column(Float, nullable=True)
    wind_speed_10m = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_hourly_city_ts", "city_id", "ts_utc"),
    )


# -------------------------
# Fact Table - Daily
# -------------------------
class FactWeatherDaily(Base):
    __tablename__ = "fact_weather_daily"

    city_id = mapped_column(Integer, primary_key=True)
    date = mapped_column(Date, primary_key=True)

    temperature_2m_max = mapped_column(Float, nullable=True)
    temperature_2m_min = mapped_column(Float, nullable=True)
    precipitation_sum = mapped_column(Float, nullable=True)
    wind_speed_10m_max = mapped_column(Float, nullable=True)
    temp_range = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_daily_city_date", "city_id", "date"),
    )


# -------------------------
# Database Init & Load Logic
# -------------------------
def init_db():
    """Create all tables if they don't exist."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def upsert_dim_city(session: Session, cities_df: pd.DataFrame):
    """Insert cities if not already present."""
    for _, r in cities_df.iterrows():
        exists = session.execute(
            text("SELECT city_id FROM dim_city WHERE city=:c"),
            {"c": r["city"]},
        ).fetchone()

        if not exists:
            session.execute(
                text("""
                    INSERT INTO dim_city (city, country, latitude, longitude, timezone)
                    VALUES (:city, :country, :lat, :lon, :tz)
                """),
                {
                    "city": r["city"],
                    "country": r.get("country"),
                    "lat": float(r["latitude"]),
                    "lon": float(r["longitude"]),
                    "tz": r.get("timezone"),
                },
            )
    session.commit()


def load_hourly(session: Session, df: pd.DataFrame):
    """Load hourly weather facts."""
    if df.empty:
        return

    cities = dict(session.execute(text("SELECT city, city_id FROM dim_city")).fetchall())
    rows = []
    for _, r in df.iterrows():
        cid = cities.get(r["city"])
        if cid is None:
            continue
        rows.append(
            {
                "city_id": cid,
                "ts_utc": pd.to_datetime(r["ts_local"]).to_pydatetime(),
                "temperature_2m": r.get("temperature_2m"),
                "relative_humidity_2m": r.get("relative_humidity_2m"),
                "apparent_temperature": r.get("apparent_temperature"),
                "precipitation": r.get("precipitation"),
                "wind_speed_10m": r.get("wind_speed_10m"),
            }
        )

    if rows:
        tmp = pd.DataFrame(rows).drop_duplicates(subset=["city_id", "ts_utc"])
        tmp.to_sql("fact_weather_hourly", session.bind, if_exists="append", index=False)


def load_daily(session: Session, df: pd.DataFrame):
    """Load daily weather facts."""
    if df.empty:
        return

    cities = dict(session.execute(text("SELECT city, city_id FROM dim_city")).fetchall())
    rows = []
    for _, r in df.iterrows():
        cid = cities.get(r["city"])
        if cid is None:
            continue
        rows.append(
            {
                "city_id": cid,
                "date": pd.to_datetime(r["date"]).date(),
                "temperature_2m_max": r.get("temperature_2m_max"),
                "temperature_2m_min": r.get("temperature_2m_min"),
                "precipitation_sum": r.get("precipitation_sum"),
                "wind_speed_10m_max": r.get("wind_speed_10m_max"),
                "temp_range": r.get("temp_range"),
            }
        )

    if rows:
        tmp = pd.DataFrame(rows).drop_duplicates(subset=["city_id", "date"])
        tmp.to_sql("fact_weather_daily", session.bind, if_exists="append", index=False)

def run_load():
    """
    Run full ETL load into PostgreSQL.
    - Initializes DB if needed
    - Clears existing fact tables to avoid duplicate key errors
    - Loads new hourly and daily data
    """
    DATA_DIR = os.getenv("DATA_DIR", "data")
    init_db()

    session = get_session()

    hourly_path = os.path.join(DATA_DIR, "processed", "hourly.parquet")
    daily_path = os.path.join(DATA_DIR, "processed", "daily.parquet")
    cities_path = os.path.join(DATA_DIR, "processed", "cities.parquet")

    # Load parquet data
    hourly = pd.read_parquet(hourly_path)
    daily = pd.read_parquet(daily_path) if os.path.exists(daily_path) else pd.DataFrame()
    cities = pd.read_parquet(cities_path)

    # Upsert city dimension
    upsert_dim_city(session, cities)

    # --- CLEAR EXISTING DATA SAFELY ---
    print("Clearing existing data from fact tables...")
    try:
        session.execute(text("TRUNCATE TABLE fact_weather_hourly RESTART IDENTITY CASCADE;"))
        session.execute(text("TRUNCATE TABLE fact_weather_daily RESTART IDENTITY CASCADE;"))
        session.commit()
        print("Tables truncated successfully.")
    except Exception as e:
        session.rollback()
        print(f"Warning: Could not truncate tables — {e}")

    # --- LOAD NEW DATA ---
    print("Loading fresh data into database...")
    try:
        load_hourly(session, hourly)
        load_daily(session, daily)
        session.commit()
        print("DB load complete.")
    except Exception as e:
        session.rollback()
        print(f"Load failed: {e}")
    finally:
        session.close()


