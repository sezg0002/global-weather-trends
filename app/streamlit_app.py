import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import plotly.express as px

# -------------------------
# Setup
# -------------------------
DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/weatherdb")
engine = create_engine(DB_URL)

st.set_page_config(page_title="Global Weather Trends", layout="wide")

st.title("🌍 Global Weather Trends Dashboard")
st.markdown("This dashboard displays air quality and weather patterns across European cities using live data from PostgreSQL.")

# -------------------------
# Data loading functions
# -------------------------
@st.cache_data(ttl=600)
def load_table(table_name):
    with engine.connect() as conn:
        df = pd.read_sql(text(f"SELECT * FROM {table_name}"), conn)
    return df

@st.cache_data(ttl=600)
def load_mart():
    query = """
    SELECT m.city_id, d.city, d.country, m.date,
           m.temperature_2m_max, m.temperature_2m_min, m.precipitation_sum, m.wind_speed_10m_max, m.temp_range
    FROM mart_city_daily_summary m
    JOIN dim_city d ON m.city_id = d.city_id
    ORDER BY m.date DESC
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df

# -------------------------
# Load data
# -------------------------
try:
    mart_df = load_mart()
    cities = mart_df["city"].unique()
except Exception as e:
    st.error(f"❌ Error loading data from database: {e}")
    st.stop()

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("Filters")
selected_city = st.sidebar.selectbox("Select City", sorted(cities))
filtered = mart_df[mart_df["city"] == selected_city]

# -------------------------
# Daily summary charts
# -------------------------
st.subheader(f"📅 Daily Weather Summary — {selected_city}")
col1, col2 = st.columns(2)

with col1:
    fig1 = px.line(filtered, x="date", y=["temperature_2m_max", "temperature_2m_min"],
                   title="Temperature (°C)", labels={"value": "°C", "variable": "Type"})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(filtered, x="date", y="precipitation_sum", title="Daily Precipitation (mm)")
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Wind chart
# -------------------------
st.subheader("💨 Max Wind Speed per Day")
fig3 = px.area(filtered, x="date", y="wind_speed_10m_max", title="Max Wind Speed (m/s)")
st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# Summary metrics
# -------------------------
st.subheader("📊 Summary Metrics")
latest = filtered.sort_values("date").iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Max Temp", f"{latest['temperature_2m_max']:.1f} °C")
col2.metric("Min Temp", f"{latest['temperature_2m_min']:.1f} °C")
col3.metric("Precipitation", f"{latest['precipitation_sum']:.1f} mm")
col4.metric("Wind Speed", f"{latest['wind_speed_10m_max']:.1f} m/s")

st.caption("Data Source: Open-Meteo API • Stored in PostgreSQL • Processed via Airflow ETL")
