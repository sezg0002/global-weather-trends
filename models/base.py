
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def get_engine():
    db_url = os.getenv("DB_URL", "sqlite:///data/warehouse/weather.db")
    if db_url.startswith("sqlite:///"):
        os.makedirs("data/warehouse", exist_ok=True)
    engine = create_engine(db_url, future=True)
    return engine

def get_session():
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)()
