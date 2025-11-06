# 🌍 Global Weather Trends Dashboard

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-green?logo=postgresql)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b?logo=streamlit)
![ETL](https://img.shields.io/badge/ETL-End--to--End-orange)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

---

## 📘 Overview

**Global Weather Trends Dashboard** is an **end-to-end Data Engineering project** that collects, processes, and visualizes real-time weather data for major European cities.  
It demonstrates the complete lifecycle of a data product — from **API ingestion to analytics and storytelling**.

Developed as part of a **University Data Engineering project** by **Harun SEZGIN**, this work focuses on data reliability, automation, and reproducibility.

---

## 🏗️ Architecture Overview

The project implements a modern **ETL + Data Warehouse + Dashboard** architecture.

![Architecture Overview](./docs/architecture.png)

### 🔍 Explanation of the Architecture

1. **Data Source — Open-Meteo API**  
   The project retrieves real-time weather data (temperature, humidity, precipitation, wind speed, etc.) for multiple European cities using the Open-Meteo public API.

2. **Extract & Transform (Python + Pandas)**  
   Python scripts query the API, clean and enrich the data, and structure it into hourly and daily datasets.

3. **Load — PostgreSQL Data Warehouse**  
   Processed data is loaded into a PostgreSQL database with a dimensional model (fact and dimension tables) for analytics and aggregation.

4. **Analytics Mart (SQL)**  
   Analytical marts are generated to simplify visualization and compute high-level metrics (temperature range, precipitation totals, etc.).

5. **Visualization — Streamlit Dashboard**  
   The data is visualized through an interactive Streamlit dashboard, providing insights into climate trends across cities.

6. **Orchestration — Docker Compose**  
   The entire workflow is containerized, ensuring reproducibility and easy deployment on any environment.


## ⚙️ Tech Stack

| Layer | Technology | Description |
|--------|-------------|-------------|
| **Extract** | Python · Requests | Querying Open-Meteo API (50k+ datapoints) |
| **Transform** | Pandas | Cleaning, aggregating, and enriching datasets |
| **Load** | SQLAlchemy · PostgreSQL | Data modeling and warehousing |
| **Analytics** | SQL | Creation of data marts for visualization |
| **Visualization** | Streamlit | Interactive weather dashboard |
| **Orchestration** | Docker Compose | Automated pipeline environment |
| **Documentation** | Markdown · GitHub | Professional project delivery |

---

## 🧠 Key Features

✅ Automated **ETL Pipeline** (Extract → Transform → Load → Analyze)  
✅ **PostgreSQL Warehouse** with dimensional modeling (fact/dim tables)  
✅ Dynamic **data marts** for aggregated insights  
✅ **Interactive Streamlit dashboard** with live charts and filters  
✅ **Dockerized** for portable and reproducible deployment  
✅ Built with **real API data** from [Open-Meteo](https://open-meteo.com)  

---

## 📂 Project Structure

```
global-weather-trends/
│
├── etl/
│   ├── extract_openmeteo.py      # Data extraction logic (API requests)
│   ├── transform_weather.py      # Cleaning and aggregation
│   ├── load_to_db.py             # Loading into PostgreSQL
│   ├── analytics.py              # Analytical marts creation
│   └── etl_pipeline.py           # Full ETL orchestration
│
├── app/
│   └── streamlit_app.py          # Streamlit dashboard app
│
├── models/
│   └── base.py                   # SQLAlchemy ORM models and DB connection
│
├── data/                         # Local raw/processed data (gitignored)
│
├── docker-compose.yml            # Full containerized setup
├── requirements.txt              # Python dependencies
├── .env.example                  # Example environment configuration
└── README.md                     # Documentation
```

---

## 🚀 Quick Start Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/HarunSezgin/global-weather-trends.git
cd global-weather-trends
```

### 2️⃣ Environment Setup
Copy the example environment file and configure it:
```bash
cp .env.example .env
```

**Example `.env`:**
```
DB_URL=postgresql+psycopg2://postgres:postgres@postgres_weather:5432/weatherdb
CITIES=Paris,London,Berlin,Madrid,Rome
OPENMETEO_BASE_URL=https://api.open-meteo.com/v1/forecast
HOURLY_VARS=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m
DAILY_VARS=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max
TIMEZONE=Europe/Paris
DATA_DIR=data
```

---

### 3️⃣ Run with Docker (Recommended)
```bash
docker compose up -d --build
```

This will:
- Start **PostgreSQL**
- Run the **ETL pipeline**
- Launch the **Streamlit dashboard**

---

### 4️⃣ Access the Dashboard
Once running, open your browser:  
👉 [http://localhost:8501](http://localhost:8501)

---

## 🧩 ETL Workflow

| Step | Module | Description |
|------|---------|-------------|
| 🟦 Extract | `extract_openmeteo.py` | Calls Open-Meteo API and stores raw JSON |
| 🟩 Transform | `transform_weather.py` | Cleans and formats hourly/daily data |
| 🟨 Load | `load_to_db.py` | Inserts clean data into PostgreSQL tables |
| 🟧 Analytics | `analytics.py` | Builds summarized marts for visualization |
| 🟥 Visualize | `streamlit_app.py` | Displays metrics, trends, and insights |

---

## 🗄️ Database Design

**Core Tables:**
- `dim_city` → Reference for cities  
- `fact_weather_hourly` → Hourly weather metrics  
- `fact_weather_daily` → Daily summaries  
- `mart_city_daily_summary` → Analytical summary for dashboards  

---

## 📊 Example Insights

- 🌡️ Temperature trends across cities  
- 💨 Wind speed distribution by region  
- 🌧️ Rainfall intensity and patterns  
- 🌆 Comparative day vs night temperatures  

All visualized interactively through **Streamlit**.

---

## 🧱 Automation (Optional: Airflow)

For advanced orchestration, this project can integrate with **Apache Airflow** to refresh data daily at 6 AM.

DAG: `weather_etl_dag.py`  
Schedule: `0 6 * * *`

*(Optional — not required for core functionality.)*

---

## 🧾 Why Not Airflow (Design Choice)

This project is orchestrated with **Docker Compose**, which provides sufficient automation for daily execution.  
Airflow is suited for large-scale multi-job pipelines; here, the goal is to **demonstrate ETL proficiency** and **deployment simplicity**.

---

## 👨‍💻 Author

**Harun SEZGIN**  
_Data Engineering Student — University Project_  
📧 Contact: (optional)  
🌐 GitHub: [HarunSezgin](https://github.com/HarunSezgin)

---

## 🧠 Key Learnings

- Building **end-to-end ETL pipelines** with Python and SQL  
- Working with **real-world API data**  
- Designing **data models and marts** for analytics  
- **Containerizing** data workflows with Docker  
- Delivering professional **data storytelling** with Streamlit  

---

## 📜 License

This project is released for **educational and demonstration purposes** only.  
© 2025 — Harun SEZGIN — University Data Engineering Project
