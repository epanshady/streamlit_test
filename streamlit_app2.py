# --------------------------------------------
# 🌧️ Malaysia Flood Risk Buddy (User-Friendly Edition)
# BVI1234 | Group VC24001 · VC24009 · VC24011
# --------------------------------------------

import streamlit as st
import pydeck as pdk
import pandas as pd
from datetime import datetime, timedelta
import requests_cache
import requests
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------
# 🌐 Setup Open-Meteo Client
# --------------------------------------------
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)

API_KEY = "1468e5c2a4b24ce7a64140429250306"

# --------------------------------------------
# 📍 City Coordinates (Flood-Prone Areas)
# --------------------------------------------
flood_map = {
    "Selangor": {
        "Shah Alam": (3.0738, 101.5183),
        # Add other cities as needed
    }
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
weather, om_rain = None, None
if confirmed:
    try:
        url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=3"
        response = requests.get(url)
        if response.status_code == 200:
            weather = response.json()
    except Exception as e:
        st.error(f"❌ WeatherAPI Error: {e}")

    try:
        result = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=auto")
        if result.status_code == 200:
            om_rain = result.json()["daily"]["precipitation_sum"]
    except Exception as e:
        st.error(f"❌ Open-Meteo Error: {e}")

# --------------------------------------------
# 📍 Map Layer with Notes
# --------------------------------------------
map_df = pd.DataFrame({"lat": [lat], "lon": [lon], "intensity": [om_rain[0] if om_rain is not None else 0]})

# Visual Rainfall Intensity Map
st.subheader("🌍 Visual Rainfall Intensity Map")

# Creating a layer to show notes when zooming in
text_layer = pdk.Layer(
    "TextLayer",
    map_df,
    get_position='[lon, lat]',
    get_text='"Rainfall: " + intensity + " mm"',
    get_size=16,
    get_color=[255, 140, 0, 255],
    pickable=True
)

# Creating a layer to show the circle marker (for zoomed-in view)
circle_layer = pdk.Layer(
    "ScatterplotLayer",
    map_df,
    get_position='[lon, lat]',
    get_radius=2000,  # Radius in meters, adjust as needed
    get_color='[255, 140, 0, 160]',
    get_fill_color='[255, 140, 0, 160]',
    pickable=True
)

# Map view state
view_state = pdk.ViewState(
    latitude=lat,
    longitude=lon,
    zoom=10,  # Adjust zoom level to ensure you're focusing on the right area
    pitch=40
)

# Adding layers to the map
deck = pdk.Deck(
    initial_view_state=view_state,
    layers=[text_layer, circle_layer],
    map_style='mapbox://styles/mapbox/satellite-v9'
)

# Render the map
st.pydeck_chart(deck)





