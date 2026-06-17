"""Global Weather Trends — analytics dashboard.

Reads the analytics mart (`mart_city_daily_summary` + `dim_city`) from the
PostgreSQL warehouse populated by the ETL pipeline and renders a dark,
recruiter-facing data dashboard: KPI cards, temperature trends, precipitation
and a cross-city comparison.
"""

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

DB_URL = os.getenv(
    "DB_URL", "postgresql+psycopg2://postgres:postgres@localhost:5434/weatherdb"
)
engine = create_engine(DB_URL)

st.set_page_config(
    page_title="Global Weather Trends — Data Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 2.2rem; max-width: 1180px; }
      h1, h2, h3 { letter-spacing: -0.015em; }
      [data-testid="stMetric"] {
        background: #161a2e; border: 1px solid rgba(255,255,255,.06);
        padding: 1rem 1.1rem; border-radius: 14px;
      }
      [data-testid="stMetricValue"] { color: #34d399; font-weight: 700; }
      .pill {
        display: inline-block; padding: .2rem .7rem; border-radius: 999px;
        font-size: .72rem; font-weight: 700; letter-spacing: .03em;
        background: rgba(99,102,241,.15); color: #a5b4fc;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

PALETTE = ["#6366f1", "#22d3ee", "#f59e0b", "#34d399", "#f472b6"]


def _style(fig, height=320):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0, title=""),
        font=dict(color="#cbd5e1"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.06)", title="")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)")
    return fig


@st.cache_data(ttl=300)
def load_mart():
    query = """
        SELECT m.city_id, d.city, d.country, m.date,
               m.temperature_2m_max, m.temperature_2m_min,
               m.precipitation_sum, m.wind_speed_10m_max, m.temp_range
        FROM mart_city_daily_summary m
        JOIN dim_city d ON m.city_id = d.city_id
        ORDER BY m.date
    """
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


# ----------------------------------------------------------------- header
head_l, head_r = st.columns([0.78, 0.22])
with head_l:
    st.title("Global Weather Trends")
    st.caption(
        "End-to-end data engineering · Open-Meteo API → PostgreSQL warehouse "
        "(fact + dimension model) → Streamlit"
    )
with head_r:
    st.markdown(
        '<div style="text-align:right;margin-top:1.3rem">'
        '<span class="pill">● ETL · LIVE DATA</span></div>',
        unsafe_allow_html=True,
    )

try:
    df = load_mart()
except Exception as exc:  # noqa: BLE001
    st.error(f"Database unavailable: {exc}")
    st.stop()

if df.empty:
    st.warning("No data in the warehouse yet — run the ETL pipeline first.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
cities = sorted(df["city"].unique())

sel = st.selectbox("City", ["All cities"] + cities, index=0)
view = df if sel == "All cities" else df[df["city"] == sel]

# -------------------------------------------------------------------- KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg max temp", f"{view['temperature_2m_max'].mean():.1f} °C")
k2.metric("Avg min temp", f"{view['temperature_2m_min'].mean():.1f} °C")
k3.metric("Total precipitation", f"{view['precipitation_sum'].sum():.0f} mm")
k4.metric("Peak wind", f"{view['wind_speed_10m_max'].max():.0f} km/h")

# ------------------------------------------------------------- temperature
st.markdown("### Temperature trend")
if sel == "All cities":
    fig_t = px.line(
        view, x="date", y="temperature_2m_max", color="city",
        color_discrete_sequence=PALETTE, line_shape="spline",
        labels={"temperature_2m_max": "Max °C"},
    )
else:
    fig_t = px.line(
        view, x="date", y=["temperature_2m_max", "temperature_2m_min"],
        color_discrete_sequence=["#6366f1", "#22d3ee"], line_shape="spline",
        labels={"value": "°C", "variable": ""},
    )
st.plotly_chart(_style(fig_t, 330), use_container_width=True)

# ---------------------------------------------- precipitation + comparison
c_left, c_right = st.columns(2)
with c_left:
    st.markdown("#### Daily precipitation")
    fig_p = px.bar(
        view, x="date", y="precipitation_sum",
        color="city" if sel == "All cities" else None,
        color_discrete_sequence=PALETTE,
        labels={"precipitation_sum": "mm"},
    )
    st.plotly_chart(_style(fig_p, 280), use_container_width=True)

with c_right:
    st.markdown("#### Avg max temperature by city")
    by_city = (
        df.groupby("city", as_index=False)["temperature_2m_max"]
        .mean()
        .sort_values("temperature_2m_max", ascending=False)
    )
    fig_c = px.bar(
        by_city, x="temperature_2m_max", y="city", orientation="h",
        color="city", color_discrete_sequence=PALETTE,
        labels={"temperature_2m_max": "Avg max °C", "city": ""},
    )
    fig_c.update_layout(showlegend=False)
    st.plotly_chart(_style(fig_c, 280), use_container_width=True)

st.divider()
st.caption(
    "Global Weather Trends — data engineering project by Harun Sezgin · "
    "github.com/sezg0002/global-weather-trends"
)
