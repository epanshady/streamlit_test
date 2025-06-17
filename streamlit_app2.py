import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import folium

# ---------- CONFIG ----------
st.set_page_config(page_title="FloodSight Malaysia", layout="wide")
WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ---------- HEADER ----------
st.title("🌧 FloodSight Malaysia")
st.markdown("### Realtime Flood Risk Forecast for Malaysian Cities")

# ---------- CITY OPTIONS (Flood-Prone Areas Only) ----------
city_coords = {
    "Kuala Lumpur": [3.139, 101.6869],
    "Shah Alam": [3.0738, 101.5183],
    "Petaling Jaya": [3.1073, 101.6067],
    "George Town (Penang)": [5.4164, 100.3327],
    "Johor Bahru": [1.4927, 103.7414],
    "Kota Bharu": [6.1254, 102.2381],
    "Kuantan": [3.8077, 103.3260],
    "Kuala Terengganu": [5.3290, 103.1370],
    "Klang": [3.0333, 101.45],
    "Muar": [2.0500, 102.5667],
    "Pasir Mas": [6.0333, 102.1333],
    "Batu Pahat": [1.8500, 102.9333]
}

# ---------- USER INPUT ----------
st.markdown("#### 🏩 Choose a city")
city = st.selectbox("Select city for flood forecast:", sorted(city_coords.keys()))

# ---------- FETCH WEATHER DATA ----------
def get_weather(city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": WEATHERAPI_KEY, "q": city}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            return {
                "temperature": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "rain": data["current"].get("precip_mm", 0),
                "time": data["location"]["localtime"]
            }
        else:
            return None
    except:
        return None

# ---------- FETCH RAINFALL HISTORY ----------
def get_rainfall_history(city):
    url = "http://api.weatherapi.com/v1/history.json"
    date_today = datetime.today().strftime('%Y-%m-%d')
    params = {"key": WEATHERAPI_KEY, "q": city, "dt": date_today}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            hours = data["forecast"]["forecastday"][0]["hour"]
            rain_by_hour = [(hour["time"], hour["precip_mm"]) for hour in hours]
            return rain_by_hour
        else:
            return []
    except:
        return []

# ---------- FLOOD RISK LOGIC ----------
def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

# ---------- PIE CHART FOR RAINFALL BREAKDOWN ----------
def plot_pie_chart(rain):
    labels = ['Heavy Rain', 'Light Rain', 'No Rain']
    sizes = [rain, 100 - rain, 0]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    st.pyplot(plt)

# ---------- MAP VISUALIZATION ----------
def plot_map():
    city_coords_map = city_coords[city]
    map = folium.Map(location=city_coords_map, zoom_start=10)
    folium.Marker(location=city_coords_map, 
                  popup=f"{city}: {risk}").add_to(map)
    st.components.v1.html(map._repr_html_(), height=600)

# ---------- RENDER ----------
st.markdown("---")
if st.button("🔍 Check Flood Risk"):
    weather = get_weather(city)

    if weather:
        st.success("✅ Weather data retrieved successfully.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="🌡 Temperature", value=f"{weather['temperature']} °C", delta=None, color="blue")
        with col2:
            st.metric(label="💧 Humidity", value=f"{weather['humidity']}%", delta=None, color="blue")
        with col3:
            st.metric(label="🌧 Rainfall", value=f"{weather['rain']} mm", delta=None, color="blue")
        st.caption(f"🕒 Data time: {weather['time']}")

        # Estimate risk
        risk = estimate_risk(weather['rain'], weather['humidity'])
        st.sidebar.header("⚠ Flood Risk Level")
        st.sidebar.markdown(f"## {risk}")

        # Pie chart for rainfall breakdown
        st.markdown("#### 🌧 Rainfall Breakdown")
        plot_pie_chart(weather["rain"])

        # Map visualization for the city
        st.markdown("#### 📍 City Location on Map")
        plot_map()

        # Summary Table
        st.markdown("#### 📈 Summary Table")
        df = pd.DataFrame([{
            "City": city,
            "Rainfall (mm)": weather["rain"],
            "Humidity (%)": weather["humidity"],
            "Temperature (°C)": weather["temperature"],
            "Flood Risk": risk
        }])
        st.dataframe(df, use_container_width=True)

        # Weather Breakdown Bar Chart
        st.markdown("#### 📊 Weather Breakdown")
        weather_df = pd.DataFrame({
            "Metric": ["Temperature (°C)", "Humidity (%)", "Rainfall (mm)"],
            "Value": [weather["temperature"], weather["humidity"], weather["rain"]],
        }).set_index("Metric")
        st.bar_chart(weather_df)

        # Hourly Rainfall History
        st.markdown("#### 🌧 Hourly Rainfall History (Area Chart)")
        rain_data = get_rainfall_history(city)
        if rain_data:
            times, rains = zip(*rain_data)
            rain_df = pd.DataFrame({"Rainfall (mm)": rains}, index=pd.to_datetime(times))
            st.area_chart(rain_df)
        else:
            st.info("No historical rainfall data available.")

    else:
        st.error("❌ Could not retrieve weather data. Check the city name or API key.")
