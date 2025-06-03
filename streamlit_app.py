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
        data = response.json()
        playlist_names = [playlist['name'] for playlist in data['playlists']['items']]
        
        # Add a dropdown to choose a playlist
        playlist_choice = st.selectbox('Choose a playlist:', playlist_names)
        
        # Fetch selected playlist details
        selected_playlist = next(playlist for playlist in data['playlists']['items'] if playlist['name'] == playlist_choice)
        
        # Show playlist details
        st.write(f"**Playlist**: {selected_playlist['name']}")
        st.write(f"**Description**: {selected_playlist['description']}")
        st.image(selected_playlist['images'][0]['url'], caption="Playlist Cover")
        
        # Simulate tracks from selected playlist
        playlist_id = selected_playlist['id']
        track_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        track_response = requests.get(track_url, headers=headers)
        
        if track_response.status_code == 200:
            tracks = track_response.json()['items']
            track_names = [track['track']['name'] for track in tracks]
            
            # Add a dropdown to choose a song
            track_choice = st.selectbox('Choose a song:', track_names)
            st.write(f"You have selected: {track_choice}")
            
            # Simulate play or add to library action
            if st.button('Play Song'):
                st.success(f"Now playing: {track_choice} from {selected_playlist['name']}")
            if st.button('Add to Library'):
                st.success(f"Added {track_choice} to your Spotify library.")
        else:
            st.error(f"Failed to fetch tracks. Error: {track_response.status_code}")
    else:
        st.error(f"Failed to fetch playlists. Error: {response.status_code}")
else:
    st.error("Unable to fetch Spotify API data.")




