# --------------------------------------------
# 🌧 Malaysia Flood Risk Buddy 
# BVI1234 | Group VC24001 · VC24009 · VC24011
# --------------------------------------------

# --- 🧠 Core Libraries & API Tools ---
import streamlit as st  # Web UI framework for building interactive user interface
import requests  # To make API calls
import pandas as pd  # Data handling for processing the forecast data
import numpy as np  # Numerical operations for simulations or calculations
import matplotlib.pyplot as plt  # Plotting pie charts for risk visualization
import pydeck as pdk  # Interactive map visualization
from datetime import datetime, timedelta  # Time management to handle dates
import requests_cache  # Cache for API requests to minimize redundant calls
from retry_requests import retry  # Retry failed requests to handle connectivity issues
from geopy.geocoders import Nominatim  # To get latitude and longitude from address input

# --- 🖼 Page Setup & Styling ---
st.set_page_config(page_title="Flood Buddy - Malaysia", page_icon="☔", layout="wide")

# Add custom CSS for button styling
st.markdown("""
<style>
.stButton button {
    background:#28a745;  # Green background color for the button
    color:#fff;  # White text color
    font-weight:bold;  # Make text bold
    border-radius:8px;  # Rounded button edges
}
</style>
""", unsafe_allow_html=True)


# --- 🔐 API Keys & Session Caching ---
API_KEY = "1468e5c2a4b24ce7a64140429250306"  # API key for WeatherAPI
NEWS_API_KEY = "pub_6b426fe08efa4436a4cd58ec988c62e0"  # API key for NewsData.io
session = retry(requests_cache.CachedSession('.cache', expire_after=3600), retries=5, backoff_factor=0.2)  # Cache session for API requests with retry
geolocator = Nominatim(user_agent="flood-buddy-app")  # Geopy geolocator to fetch latitude and longitude

# --- 🗺️ Flood-Prone Locations (Malaysia) ---
# Defining the flood-prone locations in various states of Malaysia
flood_map = {
    "Selangor": ["Shah Alam", "Petaling", "Klang", "Gombak", "Hulu Langat", "Sabak Bernam"],
    "Johor": ["Johor Bahru", "Batu Pahat", "Muar", "Kluang", "Segamat", "Kota Tinggi"],
    "Sarawak": ["Kuching", "Sibu", "Miri", "Bintulu", "Sri Aman", "Limbang"],
    "Sabah": ["Kota Kinabalu", "Sandakan", "Tawau", "Lahad Datu", "Beaufort", "Keningau"],
    "Kelantan": ["Kota Bharu", "Pasir Mas", "Tumpat", "Gua Musang", "Tanah Merah"],
    "Terengganu": ["Kuala Terengganu", "Dungun", "Kemaman", "Besut", "Setiu"],
    "Pahang": ["Kuantan", "Temerloh", "Jerantut", "Raub", "Bentong"],
    "Penang": ["George Town", "Seberang Perai", "Balik Pulau"],
    "Perak": ["Ipoh", "Taiping", "Teluk Intan", "Lumut"],
    "Negeri Sembilan": ["Seremban", "Port Dickson", "Jempol"],
    "Melaka": ["Melaka Tengah", "Alor Gajah", "Jasin"],
    "Kedah": ["Alor Setar", "Sungai Petani", "Kulim"],
    "Perlis": ["Kangar", "Arau"]
}


# --- 🧭 Sidebar: User Input ---
with st.sidebar:
    st.markdown("## 🌧️ *Flood Risk Buddy*")  # Sidebar title
    st.caption("Malaysia Flood Risk Forecast & Updates")  # Sidebar caption
    st.title("⚙️ Settings")  # Settings heading
    state = st.selectbox("State", list(flood_map.keys()))  # Dropdown for selecting state
    district = st.selectbox("District", flood_map[state])  # Dropdown for selecting district
    date = st.date_input("Forecast Date", datetime.today())  # Date input for forecast date
    coord_override = st.text_input("Or enter coords manually (lat,lon)")  # Input for custom latitude and longitude
    go = st.button("🔍 Get Forecast")  # Button to fetch forecast

# --- 🧩 Helper Functions ---
def risk_level(r):
    """
    Categorizes the rainfall into different risk levels:
    - Extreme: Rain > 50 mm
    - High: 30 < Rain <= 50 mm
    - Moderate: 10 < Rain <= 30 mm
    - Low: Rain <= 10 mm
    """
    return "Extreme" if r > 50 else "High" if r > 30 else "Moderate" if r > 10 else "Low"


def tip(l):
    """
    Provides tips based on the calculated risk level.
    Args:
    l (str): Risk level ("Extreme", "High", "Moderate", or "Low")

    Returns:
    str: Preparedness tips based on the risk level.
    """
    return {
        "Extreme": "Evacuate if needed; avoid floodwaters.",
        "High": "Charge devices; avoid low areas.",
        "Moderate": "Monitor alerts; stay indoors.",
        "Low": "Stay aware."
    }[l]


def get_coords(state, district):
    """
    Gets latitude and longitude from the location using Geopy's Nominatim service.
    Args:
    state (str): The state of the district
    district (str): The district in Malaysia

    Returns:
    tuple: Latitude and longitude of the location, or None if not found.
    """
    try:
        location = geolocator.geocode(f"{district}, {state}, Malaysia", timeout=10)
        return (location.latitude, location.longitude)
    except:
        return (None, None)


def fetch_news(search_term):
    """
    Fetches flood-related news articles based on a search term from the NewsAPI.
    Args:
    search_term (str): The keyword to search for in news articles

    Returns:
    list: List of filtered news articles related to flood in Malaysia.
    """
    try:
        r = session.get(f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={search_term}%20flood%20malaysia")
        results = r.json().get("results", [])
        keywords = ["flood", "banjir", "evacuate", "rain", "landslide", "inundation"]
        filtered = [n for n in results if any(k in n["title"].lower() for k in keywords)]
        return filtered
    except:
        return []


# --- 🌧️ Forecast Processing ---
if go:
    # Get coordinates based on user input or override
    if coord_override and "," in coord_override:
        lat, lon = map(float, coord_override.split(","))
    else:
        lat, lon = get_coords(state, district)
        if lat is None:
            st.error("Could not geolocate this district. Please enter coordinates manually.")
            st.stop()

    # 📅 Forecast window setup
    today = datetime.today()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")

    # 🌐 Forecast API
    w = session.get(f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=3").json()
    o = session.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=auto").json()

    rain = [d["day"]["totalprecip_mm"] for d in w["forecast"]["forecastday"]]
    df = pd.DataFrame({
        "Date": [d["date"] for d in w["forecast"]["forecastday"]],
        "Rain (mm)": rain,
        "Temp (°C)": [d["day"]["maxtemp_c"] for d in w["forecast"]["forecastday"]],
        "Humidity (%)": [d["day"]["avghumidity"] for d in w["forecast"]["forecastday"]],
        "Wind (kph)": [d["day"]["maxwind_kph"] for d in w["forecast"]["forecastday"]],
    })

    # --- 📊 Tabs ---
    tabs = st.tabs(["🌧️ Forecast", "🗺️ Map View", "📈 Trends", "🧭 Risk Overview", "📰 News"])

    with tabs[0]:
        # 💡 Forecast Tab
        lvl = risk_level(max(rain[0], o["daily"]["precipitation_sum"][0]))
        getattr(st, {"Extreme":"error","High":"warning","Moderate":"info","Low":"success"}[lvl])(f"{lvl} today – {tip(lvl)}")

        st.subheader("📅 3-Day Forecast")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

        # ✅ Real Past Rain Data (7 days)
        past_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        past_end = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        hist_url = (
            f"https://archive-api.open-meteo.com/v1/era5?"
            f"latitude={lat}&longitude={lon}&start_date={past_start}&end_date={past_end}"
            f"&daily=precipitation_sum&timezone=auto"
        )
        try:
            hist = session.get(hist_url).json()
            if "daily" in hist:
                df_past = pd.DataFrame({
                    "Date": hist["daily"]["time"],
                    "Rain (mm)": hist["daily"]["precipitation_sum"]
                })
                st.subheader("📊 Past Rain Data (7 days actual)")
                st.dataframe(df_past, use_container_width=True)
            else:
                st.warning("No historical data available.")
        except:
            st.error("Failed to retrieve historical rainfall.")

    with tabs[1]:
       # --- 🗺️ Map View Tab ---
# Create a DataFrame with latitude, longitude, and intensity data for the map
    data = pd.DataFrame({
    "lat": [lat],  # Latitude of the selected location
    "lon": [lon],  # Longitude of the selected location
    "intensity": [o["daily"]["precipitation_sum"][0]],  # Rainfall intensity from Open-Meteo API
    "tooltip": [f"Location: {district}, {state}\nRainfall: {o['daily']['precipitation_sum'][0]} mm"]  # Tooltip content
})

# Display the map with PyDeck's ScatterplotLayer and tooltip for interactive visualization
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=8),  # Initial map view with zoom and position
    layers=[pdk.Layer(
        "ScatterplotLayer",  # Layer type: Scatter plot
        data=data,  # Data to visualize on the map
        get_position='[lon, lat]',  # Latitude and longitude for the position
        get_color='[255, 0, 0, 100]',  # Color of the points (red with transparency)
        get_radius=10000,  # Size of the radius for each point
        pickable=True,  # Makes the points clickable for interaction
        opacity=0.3  # Transparency of the points
    )],
    tooltip={"text": "{tooltip}"}  # Display the tooltip when hovering over a point
))


    with tabs[2]:
        st.subheader("Rainfall Trend")
        st.line_chart(df.set_index("Date")["Rain (mm)"])
        st.subheader("Humidity Trend")
        st.bar_chart(df.set_index("Date")["Humidity (%)"])
        st.subheader("Wind Speed Trend")
        st.area_chart(df.set_index("Date")["Wind (kph)"])

    with tabs[3]:
        counts = df["Rain (mm)"].map(risk_level).value_counts()
        plt.figure(figsize=(6,6))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%")
        st.pyplot(plt)

    with tabs[4]:
        search_term = st.text_input("Search flood news for Malaysia:", "flood")
        if search_term:
            news = fetch_news(search_term)
            if news:
                for n in news:
                    st.markdown(f"- *{n['title']}*\n  {n.get('pubDate','')}\n  [🔗 Read more]({n['link']})")
            else:
                st.info("No relevant flood-related news articles found.")

