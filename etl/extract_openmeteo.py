
import os
import json
from datetime import datetime, timezone
from typing import Dict, List
import pandas as pd
import requests

BASE_URL = os.getenv("OPENMETEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
HOURLY_VARS = os.getenv("HOURLY_VARS", "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m")
DAILY_VARS = os.getenv("DAILY_VARS", "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Paris")
DATA_DIR = os.getenv("DATA_DIR", "data")

def load_cities() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "cities.csv")
    if not os.path.exists(path):
        raise FileNotFoundError("Missing data/cities.csv")
    df = pd.read_csv(path)
    required = {"city","country","latitude","longitude","timezone"}
    if not required.issubset(df.columns):
        raise ValueError("cities.csv missing columns")
    return df

def fetch_city_weather(lat: float, lon: float) -> Dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": HOURLY_VARS,
        "daily": DAILY_VARS,
        "timezone": TIMEZONE
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_all() -> List[str]:
    os.makedirs(os.path.join(DATA_DIR, "raw"), exist_ok=True)
    cities = load_cities()
    saved = []
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for _, row in cities.iterrows():
        payload = fetch_city_weather(row["latitude"], row["longitude"])
        fname = f"{row['city'].replace(' ','_')}_{ts}.json"
        fpath = os.path.join(DATA_DIR, "raw", fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump({"meta": row.to_dict(), "payload": payload}, f)
        saved.append(fpath)
    return saved

if __name__ == "__main__":
    files = extract_all()
    print(f"Saved {len(files)} raw snapshots to data/raw/")
