
import os, json, glob
from typing import Tuple
import pandas as pd

DATA_DIR = os.getenv("DATA_DIR", "data")

def parse_snapshot(path: str) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    meta = d["meta"]
    payload = d["payload"]
    h = payload.get("hourly", {})
    hdf = pd.DataFrame(h)
    if "time" in hdf.columns:
        hdf["ts_local"] = pd.to_datetime(hdf["time"])
        hdf.drop(columns=["time"], inplace=True)
    dly = payload.get("daily", {})
    ddf = pd.DataFrame(dly)
    if "time" in ddf.columns:
        ddf["date"] = pd.to_datetime(ddf["time"]).dt.date
        ddf.drop(columns=["time"], inplace=True)
    return hdf, ddf, meta

def transform_all():
    os.makedirs(os.path.join(DATA_DIR, "processed"), exist_ok=True)
    hourly_frames, daily_frames, meta_frames = [], [], []
    for path in glob.glob(os.path.join(DATA_DIR, "raw", "*.json")):
        hdf, ddf, meta = parse_snapshot(path)
        if not hdf.empty:
            hdf["city"] = meta["city"]
            hourly_frames.append(hdf)
        if not ddf.empty:
            if "temperature_2m_max" in ddf and "temperature_2m_min" in ddf:
                ddf["temp_range"] = ddf["temperature_2m_max"] - ddf["temperature_2m_min"]
            ddf["city"] = meta["city"]
            daily_frames.append(ddf)
        meta_frames.append(meta)
    if not hourly_frames:
        raise RuntimeError("No raw files found. Run extraction first.")
    hourly = pd.concat(hourly_frames, ignore_index=True)
    daily = pd.concat(daily_frames, ignore_index=True) if daily_frames else pd.DataFrame()
    cities = pd.DataFrame(meta_frames).drop_duplicates(subset=["city"]).reset_index(drop=True)

    hourly.to_parquet(os.path.join(DATA_DIR, "processed", "hourly.parquet"), index=False)
    if not daily.empty:
        daily.to_parquet(os.path.join(DATA_DIR, "processed", "daily.parquet"), index=False)
    cities.to_parquet(os.path.join(DATA_DIR, "processed", "cities.parquet"), index=False)
    return hourly, daily, cities

if __name__ == "__main__":
    h, d, c = transform_all()
    print("Processed parquet files written to data/processed/")
