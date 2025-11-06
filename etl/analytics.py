from sqlalchemy import text
from models.base import get_engine

def build_marts():
    """
    Create or refresh the analytics mart 'mart_city_daily_summary'.
    This view aggregates the daily weather facts into an analytics-ready table
    with standardized column names expected by the Streamlit dashboard.
    """
    engine = get_engine()
    with engine.begin() as con:
        # Drop the existing mart if it exists (to avoid schema conflicts)
        con.execute(text("DROP TABLE IF EXISTS mart_city_daily_summary"))

        # Create the mart with the proper column names
        con.execute(text("""
            CREATE TABLE mart_city_daily_summary AS
            SELECT
                f.city_id,
                f.date,
                f.temperature_2m_max AS temperature_2m_max,
                f.temperature_2m_min AS temperature_2m_min,
                f.precipitation_sum AS precipitation_sum,
                f.wind_speed_10m_max AS wind_speed_10m_max,
                f.temp_range AS temp_range
            FROM fact_weather_daily f
            JOIN dim_city d ON d.city_id = f.city_id
        """))

    print("✅ Analytics mart 'mart_city_daily_summary' built/updated.")
