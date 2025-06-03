import streamlit as st
import requests
import base64

# Set the app title
st.title('Music Playlist Finder')

# Add a welcome message
st.write('Welcome to the Music Playlist Finder')

# Create a dropdown to choose a music genre
genre_choice = st.selectbox(
    'Choose a music genre:',
    ['Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Classical']
)

# Define Spotify API endpoint and access token
client_id = '0b17a63b23f644bdb5e229651849c604'  # Your Spotify Client ID
client_secret = 'c4d460a6c8524536a44592574678a50e'  # Your Spotify Client Secret

# Get Access Token using Client ID and Client Secret
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
    # Fetch playlists based on genre (using Spotify API)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Map genre to Spotify's available genres
    genre_map = {
        'Pop': 'pop',
        'Rock': 'rock',
        'Hip-Hop': 'hiphop',
        'Jazz': 'jazz',
        'Classical': 'classical'
    }
    
    url = f'https://api.spotify.com/v1/browse/categories/{genre_map[genre_choice]}/playlists'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:





