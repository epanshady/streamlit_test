# --------------------------------------------
# 🌧 Malaysia Flood Risk Buddy 
# BVI1234 | Group VC24001 · VC24009 · VC24011
# --------------------------------------------

# --- 🧠 Core Libraries & API Tools ---
import streamlit as st                  # Web UI framework
import requests                         # API calls
import pandas as pd                     # Data handling
import numpy as np                      # Numerical ops for simulation
import matplotlib.pyplot as plt         # Plotting pie chart
import pydeck as pdk                    # Interactive mapping
from datetime import datetime, timedelta  # Time management
import requests_cache                   # Cache for API requests
from retry_requests import retry        # Retry failed requests
from geopy.geocoders import Nominatim   # Get lat/lon from address

# --- 🖼 Page Setup & Styling ---
st.set_page_config(page_title="Flood Buddy - Malaysia", page_icon="☔", layout="wide")

# Stylish button via CSS
st.markdown("""
<style>
.stButton button {
    background:#28a745;
    color:#fff;
    font-weight:bold;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# --- 🔐 API Keys & Session Caching ---
API_KEY = "1468e5c2a4b24ce7a64140429250306"  # WeatherAPI Key
NEWS_API_KEY = "pub_6b426fe08efa4436a4cd58ec988c62e0"  # NewsData.io Key
session = retry(requests_cache.CachedSession('.cache', expire_after=3600), retries=5, backoff_factor=0.2)
geolocator = Nominatim(user_agent="flood-buddy-app")

# --- 🗺️ Flood-Prone Locations (Malaysia) ---
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
    st.markdown("## 🌧️ *Flood Risk Buddy*")
    st.caption("Malaysia Flood Risk Forecast & Updates")
    st.title("⚙️ Settings")
    state = st.selectbox("State", list(flood_map.keys()))
    district = st.selectbox("District", flood_map[state])
    date = st.date_input("Forecast Date", datetime.today())
    coord_override = st.text_input("Or enter coords manually (lat,lon)")
    go = st.button("🔍 Get Forecast")

# --- 🧩 Helper Functions ---
def risk_level(r):
    """Categorize rain intensity to risk level."""
    return "Extreme" if r > 50 else "High" if r > 30 else "Moderate" if r > 10 else "Low"

def tip(l):
    """Tips based on risk level."""
    return {
        "Extreme": "Evacuate if needed; avoid floodwaters.",
        "High":     "Charge devices; avoid low areas.",
        "Moderate": "Monitor alerts; stay indoors.",
        "Low":      "Stay aware."
    }[l]

def get_coords(state, district):
    """Get coordinates from location."""
    try:
        location = geolocator.geocode(f"{district}, {state}, Malaysia", timeout=10)
        return (location.latitude, location.longitude)
    except:
        return (None, None)

def fetch_news(search_term):
    """Fetch flood-related news articles."""
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
    # Get coordinates
    if coord_override and "," in coord_override:
        lat, lon = map(float, coord_override.split(","))
    else:
        lat, lon = get_coords(state, district)
        if lat is None:
            st.error("Could not geolocate this district. Please enter coordinates manually.")
            st.stop()

    # Define forecast range
    today = datetime.today()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")  # 3-day span

    # Fetch from APIs
    w = session.get(f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=3").json()
    o = session.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=auto").json()

    # Create forecast dataframe
    rain = [d["day"]["totalprecip_mm"] for d in w["forecast"]["forecastday"]]
    df = pd.DataFrame({
        "Date": [d["date"] for d in w["forecast"]["forecastday"]],
        "Rain (mm)": rain,
        "Temp (°C)": [d["day"]["maxtemp_c"] for d in w["forecast"]["forecastday"]],
        "Humidity (%)": [d["day"]["avghumidity"] for d in w["forecast"]["forecastday"]],
        "Wind (kph)": [d["day"]["maxwind_kph"] for d in w["forecast"]["forecastday"]],
    })

    # --- 📊 Tabbed Output Sections ---
    tabs = st.tabs(["🌧️ Forecast", "🗺️ Map View", "📈 Trends", "🧭 Risk Overview", "📜 History", "📰 News"])

    with tabs[0]:
        # 💡 Forecast Tab
        lvl = risk_level(max(rain[0], o["daily"]["precipitation_sum"][0]))
        getattr(st, {"Extreme":"error","High":"warning","Moderate":"info","Low":"success"}[lvl])(f"{lvl} today – {tip(lvl)}")

        st.subheader("📅 3-Day Forecast")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

        st.subheader("📊 Past Rain Data (Mock - 7 days)")
        past_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 8)]
        past_rain = np.random.randint(5, 60, size=7)
        df_past = pd.DataFrame({"Date": past_dates[::-1], "Rain (mm)": past_rain[::-1]})
        st.dataframe(df_past, use_container_width=True)

    with tabs[1]:
        # 🌍 Map View Tab
        data = pd.DataFrame({
            "lat": [lat],
            "lon": [lon],
            "intensity": [o["daily"]["precipitation_sum"][0]],
            "tooltip": [f"Location: {district}, {state}\nRainfall: {o['daily']['precipitation_sum'][0]} mm"]
        })
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=8),
            layers=[pdk.Layer(
                "ScatterplotLayer",
                data=data,
                get_position='[lon, lat]',
                get_color='[255, 0, 0, 100]',
                get_radius=10000,
                pickable=True,
                opacity=0.3
            )],
            tooltip={"text": "{tooltip}"}
        ))

    with tabs[2]:
        # 📈 Trends Tab
        st.subheader("Rainfall Trend")
        st.line_chart(df.set_index("Date")["Rain (mm)"])
        st.subheader("Humidity Trend")
        st.bar_chart(df.set_index("Date")["Humidity (%)"])
        st.subheader("Wind Speed Trend")
        st.area_chart(df.set_index("Date")["Wind (kph)"])

    with tabs[3]:
        # 🧭 Risk Pie Chart Tab
        counts = df["Rain (mm)"].map(risk_level).value_counts()
        plt.figure(figsize=(6,6))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%")
        st.pyplot(plt)


    with tabs[4]:
        # 📰 News Feed Tab
        search_term = st.text_input("Search flood news for Malaysia:", "flood")
        if search_term:
            news = fetch_news(search_term)
            if news:
                for n in news:
                    st.markdown(f"- *{n['title']}*\n  {n.get('pubDate','')}\n  [🔗 Read more]({n['link']})")
            else:
                st.info("No relevant flood-related news articles found.")
