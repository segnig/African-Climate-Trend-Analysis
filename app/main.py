from __future__ import annotations

import streamlit as st
import plotly.express as px

from app.utils import COUNTRIES, filter_data, load_clean_data

st.set_page_config(page_title="African Climate Trend Analysis", layout="wide")
st.title("African Climate Trend Analysis Dashboard")

all_data = load_clean_data("data")

if all_data.empty:
    st.warning("No cleaned CSV files found in data/. Expected files like data/ethiopia_clean.csv")
    st.stop()

countries_display = [country.title() for country in COUNTRIES]
selected_countries = st.multiselect("Select countries", options=countries_display, default=countries_display)

min_year = int(all_data["Year"].min())
max_year = int(all_data["Year"].max())
year_range = st.slider("Select year range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

filtered = filter_data(all_data, selected_countries, year_range)

if filtered.empty:
    st.info("No data available for current filter selection.")
    st.stop()

st.subheader("Temperature Trend (Monthly Average T2M)")
monthly_t2m = filtered.groupby(["Country", "YearMonth"], as_index=False)["T2M"].mean()
fig_t2m = px.line(monthly_t2m, x="YearMonth", y="T2M", color="Country", markers=False)
fig_t2m.update_layout(xaxis_title="Month", yaxis_title="Temperature (°C)")
st.plotly_chart(fig_t2m, use_container_width=True)

st.subheader("Precipitation Distribution (PRECTOTCORR)")
fig_precip = px.box(filtered, x="Country", y="PRECTOTCORR", color="Country", points=False)
fig_precip.update_layout(xaxis_title="Country", yaxis_title="Precipitation (mm/day)", showlegend=False)
st.plotly_chart(fig_precip, use_container_width=True)
