import streamlit as st
import requests

# Set the app title
st.title("IP Geolocation Info")

# Input field for IP address
ip = st.text_input("Enter an IP address (or leave blank for your own IP):")

# Use your API key here
api_key = c08ee6a8c5764a10b465669e594dd52b
 

# If the user provides an IP address
if ip:
    url = f"https://ipgeolocation.io/ip-location/{ip}?apiKey={api_key}"
    response = requests.get(url)
    
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
        
# If the input is empty, fetch the user's own IP location
else:
    st.write("Fetching your current IP location...")
    url = f"https://ipgeolocation.io/ip-location?apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Display user's IP location info
        st.write(f"**Country**: {data['country_name']}")
        st.write(f"**City**: {data['city']}")
        st.write(f"**Region**: {data['state_prov']}")
        st.write(f"**Latitude**: {data['latitude']}")
        st.write(f"**Longitude**: {data['longitude']}")
        st.write(f"**ISP**: {data['isp']}")
        st.write(f"**Time Zone**: {data['timezone']['name']}")
        st.write(f"**IP**: {data['ip']}")
    else:
        st.error(f"Error fetching your location info: {response.status_code}")


