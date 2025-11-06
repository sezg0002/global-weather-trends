
import time
import schedule
from etl.etl_pipeline import main

def daily_job():
    print("Running daily ETL...")
    main()

schedule.every().day.at("06:00").do(daily_job)

if __name__ == "__main__":
    print("Scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(1)
