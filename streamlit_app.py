import streamlit as st
import requests

# Set page config
st.set_page_config(page_title="IP Geolocation Info", layout="centered")

# Title
st.title("🌍 IP Geolocation Info")

# API key
api_key = "c08ee6a8c5764a10b465669e594dd52b"

# User input for IP address
ip = st.text_input("Enter an IP address (or leave blank for your own IP):")

# If user provides an IP, make an API call
if ip:
    # API Call for a specific IP
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip}"
    response = requests.get(url)
else:
    # API Call for the user's current IP
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}"
    response = requests.get(url)

# Check if the API call was successful
if response.status_code == 200:
    data = response.json()

    # Display geolocation info
    st.write(f"**Country**: {data['country_name']}")
    st.write(f"**City**: {data['city']}")
    st.write(f"**Region**: {data['state_prov']}")
    st.write(f"**Latitude**: {data['latitude']}")
    st.write(f"**Longitude**: {data['longitude']}")
    st.write(f"**ISP**: {data['isp']}")
    st.write(f"**Time Zone**: {data['timezone']['name']}")
    st.write(f"**IP**: {data['ip']}")
else:
    st.error(f"Error fetching location info: {response.status_code}")

