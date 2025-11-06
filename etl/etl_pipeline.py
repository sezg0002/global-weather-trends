from etl.extract_openmeteo import extract_all
from etl.transform_weather import transform_all
from etl.load_to_db import run_load
from etl.analytics import build_marts


def main():
    print("Extracting...")
    extract_all()
    print("Transforming...")
    transform_all()
    print("Loading...")
    run_load()
    print("Analytics...")
    build_marts()
    print("Done.")


if __name__ == "__main__":
    main()
