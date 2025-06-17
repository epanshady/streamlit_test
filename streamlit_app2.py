# --------------------------------------------
# 🌧️ Malaysia Flood Risk Buddy (User-Friendly Edition)
# BVI1234 | Group VC24001 · VC24009 · VC24011
# --------------------------------------------

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import numpy as np
from datetime import datetime
import requests_cache
from retry_requests import retry
import matplotlib.pyplot as plt

# --------------------------------------------
# 🎨 Page Setup
# --------------------------------------------
st.set_page_config(
    page_title="🌧️ Flood Buddy - Interactive",
    page_icon="☔",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #eef3f9; }
    .stButton button { background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; }
    .stSelectbox label, .stDateInput label, .stTextInput label { font-weight: bold; }
    .stTabs [data-baseweb="tab"] button { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------
# 🌐 Setup Open-Meteo Client
# --------------------------------------------
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

API_KEY = "1468e5c2a4b24ce7a64140429250306"

# --------------------------------------------
# 📍 City Coordinates (Flood-Prone Areas)
# --------------------------------------------
flood_map = {
    "Selangor": {
        "Shah Alam": (3.0738, 101.5183), "Klang": (3.0339, 101.4455),
        "Kajang": (2.9935, 101.7871), "Gombak": (3.2986, 101.7250),
        "Puchong": (3.0250, 101.6167), "Ampang": (3.1500, 101.7667)
    },
    "Johor": {
        "Johor Bahru": (1.4927, 103.7414), "Batu Pahat": (1.8500, 102.9333),
        "Kluang": (2.0326, 103.3180), "Muar": (2.0500, 102.5667),
        "Kota Tinggi": (1.7333, 103.9000), "Pontian": (1.4833, 103.3833)
    },
    # Add other states and cities as necessary
}

# --------------------------------------------
# 🪯 Welcome Panel
# --------------------------------------------
st.title("🌊 Your Personal Flood Buddy Risk-Check")
st.markdown("Get real-time info, forecast, and visualize flood-prone conditions in Malaysia. Easy to use, fun to explore!")

st.markdown("---")

st.subheader("📍 Location & Date Settings")
col1, col2, col3 = st.columns(3)
with col1:
    selected_state = st.selectbox("🗺️ Choose State", list(flood_map.keys()))
with col2:
    selected_city = st.selectbox("🏠 Choose City", list(flood_map[selected_state].keys()))
with col3:
    selected_date = st.date_input("🖖️ Pick a Date to Check Forecast", datetime.today())

custom_location = st.text_input("🧱 Or type your own location (latitude,longitude) for more control")
latlon = custom_location.split(',') if custom_location else []

if len(latlon) == 2:
    try:
        lat, lon = float(latlon[0]), float(latlon[1])
    except:
        st.warning("⚠️ Format Error. Try: 3.0738,101.5183")
        lat, lon = flood_map[selected_state][selected_city]
else:
    lat, lon = flood_map[selected_state][selected_city]

confirmed = st.button("🔍 Get My Forecast")

# --------------------------------------------
# 📡 Weather Fetch Logic
# --------------------------------------------
def risk_level(rain):
    if rain > 50:
        return "🔴 Extreme"
    elif rain > 30:
        return "🟠 High"
    elif rain > 10:
        return "🟡 Moderate"
    else:
        return "🟢 Low"

def preparedness_tips(level):
    if level == "🔴 Extreme":
        return "Evacuate if needed, keep emergency kit ready, avoid floodwaters."
    elif level == "🟠 High":
        return "Charge devices, prepare emergency contact list, avoid travel in low areas."
    elif level == "🟡 Moderate":
        return "Monitor local alerts, keep essentials ready, stay indoors during rain."
    else:
        return "Stay informed and maintain general awareness."

weather, om_rain, historical_data = None, None, None
if confirmed:
    try:
        # Fetch Forecast Data (Future)
        url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=14"
        response = requests.get(url)
        if response.status_code == 200:
            weather = response.json()
    except Exception as e:
        st.error(f"❌ WeatherAPI Error: {e}")

    try:
        # Fetch Historical Data (Past) for the past 7 days
        historical_url = f"https://api.weatherapi.com/v1/history.json?key={API_KEY}&q={lat},{lon}&dt={selected_date.strftime('%Y-%m-%d')}"
        historical_response = requests.get(historical_url)
        if historical_response.status_code == 200:
            historical_data = historical_response.json()
    except Exception as e:
        st.error(f"❌ Historical Data Error: {e}")

# --------------------------------------------
# ⚠️ Risk Alerts
# --------------------------------------------
def show_alert_box():
    if weather and om_rain is not None:
        rain_api = weather["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
        rain_om = om_rain[0]
        combined = max(rain_api, rain_om)
        level = risk_level(combined)
        if level == "🔴 Extreme":
            st.error("🚨 EXTREME RAINFALL! Take action immediately!")
        elif level == "🟠 High":
            st.warning("⚠️ Heavy rainfall expected. Be alert.")
        elif level == "🟡 Moderate":
            st.info("🔎 Moderate rain. Keep watch.")
        else:
            st.success("✅ Low rainfall. All clear.")

        st.markdown(f"### 🎓 Preparedness Tip: {preparedness_tips(level)}")

# --------------------------------------------
# 📊 Interactive Tabs
# --------------------------------------------
if confirmed and weather:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗕️ Forecast Calendar", "🗺️ Live Map", "📈 Trend Charts", "📅 Flood Risk Pie", "📈 Historical Comparison"])

    with tab1:
        show_alert_box()
        st.write("### 🧾 14-Day Forecast Overview")
        
        # Combine Forecast and Historical Data
        forecast_df = pd.DataFrame({
            "Date": [f["date"] for f in weather["forecast"]["forecastday"]],
            "Rainfall (mm)": [f["day"]["totalprecip_mm"] for f in weather["forecast"]["forecastday"]],
            "Max Temp (°C)": [f["day"]["maxtemp_c"] for f in weather["forecast"]["forecastday"]],
            "Humidity (%)": [f["day"]["avghumidity"] for f in weather["forecast"]["forecastday"]],
            "Wind (kph)": [f["day"]["maxwind_kph"] for f in weather["forecast"]["forecastday"]]
        })
        
        # For Historical Data, we'll assume it's the data for selected_date, you can modify it as per your needs.
        if historical_data:
            historical_df = pd.DataFrame({
                "Date": [historical_data["forecast"]["forecastday"][0]["date"]],
                "Rainfall (mm)": [historical_data["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]],
                "Max Temp (°C)": [historical_data["forecast"]["forecastday"][0]["day"]["maxtemp_c"]],
                "Humidity (%)": [historical_data["forecast"]["forecastday"][0]["day"]["avghumidity"]],
                "Wind (kph)": [historical_data["forecast"]["forecastday"][0]["day"]["maxwind_kph"]]
            })
            
            # Append historical data to forecast data
            forecast_df = pd.concat([forecast_df, historical_df], ignore_index=True)
        
        st.dataframe(forecast_df, use_container_width=True)

    with tab2:
        st.subheader("🌍 Visual Rainfall Intensity Map")
        map_df = pd.DataFrame({"lat": [lat], "lon": [lon], "intensity": [om_rain[0] if om_rain is not None else 0]})
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/satellite-v9',
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=8, pitch=40),
            layers=[
                pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_color='[255, 140, 0, 160]', get_radius=5000),
                pdk.Layer("HeatmapLayer", data=map_df, get_position='[lon, lat]', aggregation='MEAN', get_weight='intensity')
            ]
        ))

    # Other tabs will remain as in the original code



