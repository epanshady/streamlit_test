import streamlit as st
import requests
import base64

# Set the app title
st.title('Music Playlist Finder')

# Add a welcome message
st.write('Welcome to the Music Playlist Finder')

# Create a dropdown to choose a music genre (based on available categories)
genre_choice = st.selectbox(
    'Choose a music category:',
    ['Made For You', 'New Releases', 'Hip-Hop', 'Country', 'Pop', 'Latin', 'Charts', 'Rock', 'R&B', 'Dance/Electronic', 'Black Music Month 2025', 'Spring', 'Workout', 'Mood', 'Party', 'Love', 'Disney', 'Netflix', 'Chill', 'Summer']
)

# Define Spotify API endpoint and access token
client_id = '0b17a63b23f644bdb5e229651849c604'  # Your Spotify Client ID
client_secret = 'c4d460a6c8524536a44592574678a50e'  # Your Spotify Client Secret

# Function to get Access Token from Spotify
def get_spotify_token(client_id, client_secret):
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        st.error("Failed to get access token")
        return None

# Get the token
access_token = get_spotify_token(client_id, client_secret)

if access_token:
    # Fetch categories using Spotify API
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    url = 'https://api.spotify.com/v1/browse/categories'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        available_categories = [category['name'] for category in data['categories']['items']]
        st.write(f"Available categories: {', '.join(available_categories)}")  # Show available categories for debugging
        
        # Check if the selected category exists in available categories
        if genre_choice in available_categories:
            category_url = f'https://api.spotify.com/v1/browse/categories/{genre_choice.lower().replace(" ", "_")}/playlists'
            category_response = requests.get(category_url, headers=headers)
            
            if category_response.status_code == 200:
                category_data = category_response.json()
                playlist_names = [playlist['name'] for playlist in category_data['playlists']['items']]
                
                # Add a dropdown to choose a playlist
                playlist_choice = st.selectbox('Choose a playlist:', playlist_names)
                
                # Fetch selected playlist details
                selected_playlist = next(playlist for playlist in category_data['playlists']['items'] if playlist['name'] == playlist_choice)
                
                # Show playlist details
                st.write(f"**Playlist**: {selected_playlist['name']}")
                st.write(f"**Description**: {selected_playlist['description']}")
                st.image(selected_playlist['images'][0]['url'], caption="Playlist Cover")
            else:
                st.error(f"Failed to fetch playlists. Error: {category_response.status_code}")
        else:
            st.error(f"The selected category '{genre_choice}' is not available. Please choose from the available categories.")
    else:
        st.error(f"Failed to fetch categories. Error: {response.status_code}")
else:
    st.error("Unable to fetch Spotify API data.")

