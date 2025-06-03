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
        available_genres = [category['name'] for category in data['categories']['items']]
        st.write(f"Available genres: {', '.join(available_genres)}")  # Show available genres to debug
        
        # Check if the selected genre exists in available genres
        if genre_choice in available_genres:
            genre_map = {  # Mapping genres to Spotify categories
                'Pop': 'pop',
                'Rock': 'rock',
                'Hip-Hop': 'hiphop',
                'Jazz': 'jazz',
                'Classical': 'classical'
            }
            genre_code = genre_map[genre_choice]
            genre_url = f'https://api.spotify.com/v1/browse/categories/{genre_code}/playlists'
            genre_response = requests.get(genre_url, headers=headers)
            
            if genre_response.status_code == 200:
                genre_data = genre_response.json()
                playlist_names = [playlist['name'] for playlist in genre_data['playlists']['items']]
                # Add a dropdown to choose a playlist
                playlist_choice = st.selectbox('Choose a playlist:', playlist_names)
                
                # Fetch selected playlist details
                selected_playlist = next(playlist for playlist in genre_data['playlists']['items'] if playlist['name'] == playlist_choice)
                # Show playlist details
                st.write(f"**Playlist**: {selected_playlist['name']}")
                st.write(f"**Description**: {selected_playlist['description']}")
                st.image(selected_playlist['images'][0]['url'], caption="Playlist Cover")
            else:
                st.error(f"Failed to fetch playlists. Error: {genre_response.status_code}")
        else:
            st.error(f"The selected genre '{genre_choice}' is not available. Please choose from the available genres.")
    else:
        st.error(f"Failed to fetch categories. Error: {response.status_code}")
else:
    st.error("Unable to fetch Spotify API data.")


