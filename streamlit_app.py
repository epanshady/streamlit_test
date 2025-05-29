import streamlit as st
import requests

# Set the app title 
st.title('Movie Ticket Booking Simulation')

# Add a welcome message 
st.write('Welcome to the Movie Ticket Booking System')

# Create a dropdown to choose a movie genre
genre_choice = st.selectbox(
    'Choose a movie genre:',
    ['Action', 'Comedy', 'Drama', 'Horror', 'Romance']
)

# Map genre to TMDb genre IDs
genre_map = {
    'Action': 28,
    'Comedy': 35,
    'Drama': 18,
    'Horror': 27,
    'Romance': 10749
}

# Fetch popular movies based on genre
api_key = 'YOUR_TMDB_API_KEY'  # Replace with your TMDb API key
url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_map[genre_choice]}'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    movie_titles = [movie['title'] for movie in data['results']]
    
    # Add a dropdown to choose a movie
    movie_choice = st.selectbox('Choose a movie:', movie_titles)
    
    # Fetch selected movie details
    selected_movie = next(movie for movie in data['results'] if movie['title'] == movie_choice)
    
    # Show movie details
    st.write(f"**Title**: {selected_movie['title']}")
    st.write(f"**Overview**: {selected_movie['overview']}")
    st.write(f"**Release Date**: {selected_movie['release_date']}")
    st.image(f"https://image.tmdb.org/t/p/w500{selected_movie['poster_path']}", caption="Movie Poster")
    
    # Simulate showtimes
    showtimes = ['10:00 AM', '1:00 PM', '4:00 PM', '7:00 PM']
    showtime_choice = st.selectbox('Choose a showtime:', showtimes)
    st.write(f"You have selected the showtime: {showtime_choice}")
    
    # Simulate seat selection
    seats = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3']
    seat_choice = st.selectbox('Choose your seat:', seats)
    st.write(f"You have selected seat: {seat_choice}")
    
    # Simulate booking confirmation
    if st.button('Confirm Booking'):
        st.success(f"Your booking is confirmed for {movie_choice} at {showtime_choice}, seat {seat_choice}. Enjoy the movie!")
else:
    st.error(f"API call failed with status code: {response.status_code}")

    st.error(f"API call failed with status code: {response.status_code}")




