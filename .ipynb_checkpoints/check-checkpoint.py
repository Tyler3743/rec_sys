import requests

api_key = "37aa7e398fc505cdf4169bded99efe8c"
movie_id = 12610

def get_movie_trailer(movie_id, api_key):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()

    # Lọc video có type = "Trailer" và site = "YouTube"
    trailers = [
        f"https://www.youtube.com/watch?v={video['key']}"
        for video in data.get("results", [])
        if video.get("type") == "Trailer" and video.get("site") == "YouTube"
    ]

    return trailers if trailers else None


# Lấy thông tin cơ bản
url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
response = requests.get(url)
movie_data = response.json()

# Ghép link poster
poster_path = movie_data.get("poster_path")
poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

# In thông tin
print(f"Title: {movie_data.get('title', 'N/A')}")
print(f"Overview: {movie_data.get('overview', 'N/A')}")
print(f"Release Date: {movie_data.get('release_date', 'N/A')}")
print(f"Rating: {movie_data.get('vote_average', 'N/A')}")
print(f"Genres: {[genre['name'] for genre in movie_data.get('genres', [])]}")
print(f"Duration: {movie_data.get('runtime', 'N/A')} minutes")
print(f"Poster URL: {poster_url}")

# Lấy trailer
trailers = get_movie_trailer(movie_id, api_key)
if trailers:
    print("🎬 Trailers:")
    # for t in trailers:
    #     #     print("-", t)
    print(trailers)
else:
    print("No trailer found.")
