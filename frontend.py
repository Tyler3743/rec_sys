import streamlit as st
import requests
import pandas as pd
import warnings

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

warnings.filterwarnings('ignore')


TMDB_API_KEY = "37aa7e398fc505cdf4169bded99efe8c"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


st.set_page_config(
    page_title="Movies.io - Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)


if 'script_run_context' not in st.session_state:
    st.session_state.script_run_context = True
if 'get_recommendations' not in st.session_state:
    st.session_state.get_recommendations = False
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'recommendations'  # 'recommendations' or 'similar'
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None
if 'similar_movies' not in st.session_state:
    st.session_state.similar_movies = []
if 'recommendation_method' not in st.session_state:
    st.session_state.recommendation_method = 'content_based'  # 'content_based' or 'collaborative'



def get_movie_details(tmdb_id=None, title=None):
    """Lấy thông tin chi tiết phim từ TMDB API ưu tiên theo tmdbId; fallback theo title."""
    try:
        # Ưu tiên lấy theo tmdb_id
        if tmdb_id is not None and pd.notna(tmdb_id):
            detail_url = f"{TMDB_BASE_URL}/movie/{int(tmdb_id)}"
            detail_params = {
                'api_key': TMDB_API_KEY,
                'language': 'en-US'
            }
            detail_response = requests.get(detail_url, params=detail_params)
            if detail_response.status_code == 200:
                movie_data = detail_response.json()
                return {
                    'title': movie_data.get('title', title or ''),
                    'overview': movie_data.get('overview', 'No overview available.'),
                    'release_date': movie_data.get('release_date', 'Unknown'),
                    'rating': movie_data.get('vote_average', 0),
                    'genres': [genre['name'] for genre in movie_data.get('genres', [])],
                    'duration': movie_data.get('runtime', 0),
                    'poster_url': f"{TMDB_IMAGE_BASE_URL}{movie_data.get('poster_path', '')}" if movie_data.get(
                        'poster_path') else None

                }


        if title:
            search_url = f"{TMDB_BASE_URL}/search/movie"
            params = {
                'api_key': TMDB_API_KEY,
                'query': title,
                'language': 'en-US',
                'page': 1
            }
            response = requests.get(search_url, params=params)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    movie_id = results[0]['id']
                    detail_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
                    detail_params = {
                        'api_key': TMDB_API_KEY,
                        'language': 'en-US'
                    }
                    detail_response = requests.get(detail_url, params=detail_params)
                    if detail_response.status_code == 200:
                        movie_data = detail_response.json()
                        return {
                            'title': movie_data.get('title', title),
                            'overview': movie_data.get('overview', 'No overview available.'),
                            'release_date': movie_data.get('release_date', 'Unknown'),
                            'rating': movie_data.get('vote_average', 0),
                            'genres': [genre['name'] for genre in movie_data.get('genres', [])],
                            'duration': movie_data.get('runtime', 0),
                            'poster_url': f"{TMDB_IMAGE_BASE_URL}{movie_data.get('poster_path', '')}" if movie_data.get(
                                'poster_path') else None
                        }
    except Exception as e:
        st.error(f"Error fetching movie details: {str(e)}")

    return None


def get_recommendations_from_api(user_id, top_n, method='content_based'):
    """Lấy recommendations từ FastAPI backend dựa trên phương pháp được chọn"""
    try:
        if method == 'content_based':

            response = requests.get(f"http://localhost:8000/recommendations?user_id={user_id}&top_n={top_n}")
        else:

            response = requests.get(f"http://localhost:8001/recommendations1?user_id={user_id}&top_n={top_n}")

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error(f"User ID {user_id} không tồn tại trong hệ thống!")
            return []
        else:
            st.error(f"Lỗi API: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        if method == 'content_based':
            st.error("Không thể kết nối đến Content-Based API server. Hãy chạy: uvicorn main:app --reload")
        else:
            st.error(
                "Không thể kết nối đến Collaborative Filtering API server. Hãy chạy: uvicorn main2:app --reload --port 8001")
        return []
    except Exception as e:
        st.error(f"Lỗi: {str(e)}")
        return []


def get_similar_movies_from_api(movie_id, top_n=10):
    """Lấy phim tương tự từ FastAPI backend (chỉ từ content-based API)"""
    try:
        response = requests.get(f"http://localhost:8000/similar_movies/{movie_id}?top_n={top_n}")

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error(f"Movie ID {movie_id} không tồn tại trong hệ thống!")
            return None
        else:
            st.error(f"Lỗi API: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Không thể kết nối đến FastAPI server. Hãy chạy: uvicorn main:app --reload")
        return None
    except Exception as e:
        st.error(f"Lỗi: {str(e)}")
        return None


def get_movie_trailer_from_tmdb(tmdb_id, api_key):
    try:
        if tmdb_id is None or pd.isna(tmdb_id):
            return None
        url = f"{TMDB_BASE_URL}/movie/{int(tmdb_id)}/videos"
        params = {'api_key': api_key, 'language': 'en-US'}
        r = requests.get(url, params=params, timeout=8)
        if r.status_code != 200:
            return None
        videos = r.json().get('results', [])
        trailer = next((v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube'), None)
        if not trailer:
            trailer = next((v for v in videos if v.get('type') == 'Teaser' and v.get('site') == 'YouTube'), None)
        return f"https://www.youtube.com/watch?v={trailer['key']}" if trailer and trailer.get('key') else None
    except Exception:
        return None


# Xử lý khi click Watch Now
def handle_watch_now(movie):
    st.session_state.view_mode = 'similar'
    st.session_state.selected_movie = movie
    # Lấy phim tương tự
    similar_data = get_similar_movies_from_api(movie['movieId'], 10)
    if similar_data:
        st.session_state.similar_movies = similar_data['similar_movies']
    st.rerun()


# Header
st.markdown("""
<div class="header-container">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
        <div style="display: flex; align-items: center; gap: 2rem;">
            <div class="logo">🎬 Movies.io</div>     
            <a href="#" class="nav-link active">Movies</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content
st.markdown("<br>", unsafe_allow_html=True)

# Sidebar cho user input
with st.sidebar:
    st.markdown("## 🎯 Movie Recommendations")

    # Lựa chọn phương pháp gợi ý
    st.markdown("### 🔧 Recommendation Method")
    recommendation_method = st.radio(
        "Chọn phương pháp gợi ý:",
        options=['content_based', 'collaborative'],
        format_func=lambda
            x: "🎭 Gợi ý theo nội dung (Content-Based)" if x == 'content_based' else "👥 Gợi ý cộng tác (Collaborative Filtering)",
        index=0 if st.session_state.recommendation_method == 'content_based' else 1,
        key="recommendation_method_radio"
    )

    # Cập nhật session state khi có thay đổi
    if recommendation_method != st.session_state.recommendation_method:
        st.session_state.recommendation_method = recommendation_method
        st.rerun()

    st.markdown("---")


    if st.session_state.view_mode == 'recommendations':
        st.markdown("### 📝 User Input")
        st.markdown("Enter a user ID to get personalized movie recommendations:")
        user_id = st.number_input("User ID", min_value=1, value=1, step=1)
        top_n = st.slider("Number of recommendations", min_value=1, max_value=20, value=4)


        if st.session_state.recommendation_method == 'content_based':
            st.info(
                "🎭 **Content-Based Filtering**: Gợi ý phim dựa trên thể loại và đặc điểm của các phim bạn đã thích.")
        else:
            st.info("👥 **Collaborative Filtering**: Gợi ý phim dựa trên sở thích của những người dùng tương tự bạn.")

        if st.button("Get Recommendations", type="primary"):
            st.session_state.view_mode = 'recommendations'
            st.session_state.get_recommendations = True
            st.session_state.user_id = user_id
            st.session_state.top_n = top_n
            st.rerun()


    elif st.session_state.view_mode == 'similar':
        if st.session_state.selected_movie:
            st.markdown(f"### Similar to: {st.session_state.selected_movie.get('title', 'Selected Movie')}")


            similar_count = st.slider("Number of similar movies", min_value=1, max_value=20, value=10)

            if st.button("Update Similar Movies", type="primary"):

                movie_id = st.session_state.selected_movie.get('movieId')
                if movie_id:
                    similar_data = get_similar_movies_from_api(movie_id, similar_count)
                    if similar_data and 'similar_movies' in similar_data:
                        st.session_state.similar_movies = similar_data['similar_movies'] or []
                    st.rerun()


        if st.button("Back to Recommendations"):
            st.session_state.view_mode = 'recommendations'
            st.rerun()



def display_movie_detail(movie_details, trailer_url=None):

    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Movie poster section
        if movie_details['poster_url']:
            st.markdown(f"""
            <div style="text-align: center;">
                <img src="{movie_details['poster_url']}" 
                     style="width: 300px; height: 450px; border-radius: 0.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.3); object-fit: cover;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center;">
                <img src="https://via.placeholder.com/300x450/1a1f2e/ffffff?text=No+Poster" 
                     style="width: 300px; height: 450px; border-radius: 0.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


        if trailer_url:
            st.markdown(f"""
            <div style="text-align:center;">
                <a href="{trailer_url}" target="_blank" class="action-btn" style="display:inline-block; width: 100%; text-align:center; text-decoration:none;">🎬 Watch</a>
            </div>
            """, unsafe_allow_html=True)
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <button class="action-btn" style="width: 100%;">
                    🎬 No film Available
                </button>
                """, unsafe_allow_html=True)

    with col_right:

        st.markdown(f'<div class="movie-title">{movie_details["title"]}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)


        st.markdown("### STORYLINE")
        st.markdown(f"""
        <div class="info-card">
            {movie_details['overview']}
        </div>
        """, unsafe_allow_html=True)


        st.markdown("### Movie Information")

        col_rating, col_year = st.columns(2)
        with col_rating:
            st.markdown(f'<div class="info-card">Rating: {movie_details["rating"]:.1f}/10</div>',
                        unsafe_allow_html=True)
        with col_year:
            st.markdown(f'<div class="info-card">Release Date: {movie_details["release_date"]}</div>',
                        unsafe_allow_html=True)

        col_genres, col_duration = st.columns(2)
        with col_genres:
            genres_str = ", ".join(movie_details["genres"])
            st.markdown(f'<div class="info-card">Genres: {genres_str}</div>', unsafe_allow_html=True)
        with col_duration:
            duration_str = f"{movie_details['duration']} minutes" if movie_details[
                                                                         'duration'] > 0 else "Unknown"
            st.markdown(f'<div class="info-card">Duration: {duration_str}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)



def display_movie_in_list(rec, col):
    with col:
        rec_details = get_movie_details(tmdb_id=rec.get('tmdbId'), title=rec.get('title'))
        if rec_details:
            poster_url = rec_details['poster_url'] or "https://via.placeholder.com/80x120/1a1f2e/ffffff?text=No+Poster"
            genres_str = ", ".join(rec_details['genres'][:2]) if rec_details['genres'] else "Unknown"

            # Create a unique key for this button based on movie ID
            watch_now_key = f"watch_now_{rec['movieId']}"

            st.markdown(f"""
            <div style="background-color: #1a1f2e; padding: 1rem; border-radius: 0.5rem; border: 1px solid #2d3748; margin-bottom: 1rem;">
                <div style="display: flex; gap: 1rem;">
                    <img src="{poster_url}" style="width: 80px; height: 120px; border-radius: 0.375rem; object-fit: cover;">
                    <div style="flex: 1;">
                        <div style="font-weight: bold; color: white; margin-bottom: 0.5rem;">{rec_details['title']}</div>
                        <div style="color: #a0aec0; font-size: 0.875rem; margin-bottom: 0.25rem;">Rating: {rec_details['rating']:.1f}/10</div>
                        <div style="color: #a0aec0; font-size: 0.875rem; margin-bottom: 0.25rem;">Genre: {genres_str}</div>
                        <div style="color: #a0aec0; font-size: 0.875rem; margin-bottom: 0.5rem;">Release: {rec_details['release_date']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Watch Now", key=watch_now_key):
                handle_watch_now(rec)


if st.session_state.view_mode == 'recommendations' and hasattr(st.session_state,
                                                               'get_recommendations') and st.session_state.get_recommendations:
    user_id = st.session_state.user_id
    top_n = st.session_state.top_n
    method = st.session_state.recommendation_method

    method_name = "Content-Based Filtering" if method == 'content_based' else "Collaborative Filtering"
    st.markdown(f"### 🎯 Recommendations using {method_name}")

    recommendations = get_recommendations_from_api(user_id, top_n, method)

    if recommendations:
        st.success(f"✅ Found {len(recommendations)} recommendations for User {user_id} using {method_name}!")


        top_movie = recommendations[0]
        movie_details = get_movie_details(tmdb_id=top_movie.get('tmdbId'), title=top_movie.get('title'))

        if movie_details:
            trailer_url = get_movie_trailer_from_tmdb(top_movie.get('tmdbId'), TMDB_API_KEY)
            display_movie_detail(movie_details, trailer_url)
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("## 🎬 Recommended Movies")
            st.markdown(f"**Top {len(recommendations)} recommendations for User {user_id} using {method_name}:**")

            for i in range(1, len(recommendations), 2):
                col1, col2 = st.columns(2)
                if i < len(recommendations):
                    display_movie_in_list(recommendations[i], col1)
                if i + 1 < len(recommendations):
                    display_movie_in_list(recommendations[i + 1], col2)
        else:
            st.error("Không thể lấy thông tin chi tiết phim từ TMDB API")
    else:
        st.warning("⚠️ Không tìm thấy recommendations cho user này.")

elif st.session_state.view_mode == 'similar' and st.session_state.selected_movie:
    selected_movie = st.session_state.selected_movie
    similar_movies = st.session_state.similar_movies
    movie_details = get_movie_details(tmdb_id=selected_movie.get('tmdbId'), title=selected_movie.get('title'))

    if movie_details:
        trailer_url = get_movie_trailer_from_tmdb(selected_movie.get('tmdbId'), TMDB_API_KEY)
        display_movie_detail(movie_details, trailer_url)
        if similar_movies:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("## 🎭 Similar Movies")
            st.markdown(f"**Movies similar to '{selected_movie.get('title', 'Selected Movie')}':**")

            for i in range(0, len(similar_movies), 2):
                col1, col2 = st.columns(2)

                if i < len(similar_movies):
                    display_movie_in_list(similar_movies[i], col1)

                if i + 1 < len(similar_movies):
                    display_movie_in_list(similar_movies[i + 1], col2)
        else:
            st.warning("⚠️ Không tìm thấy phim tương tự.")
    else:
        st.error("Không thể lấy thông tin chi tiết phim từ TMDB API")
else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem;">
        <h1 style="color: #ffffff; font-size: 3rem; margin-bottom: 1rem;">🎬 Welcome to Movies.io</h1>
        <p style="color: #a0aec0; font-size: 1.25rem; margin-bottom: 2rem;">
            Discover your next favorite movie with our advanced recommendation system
        </p>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; margin: 2rem auto; max-width: 600px;">
            <h3 style="color: white; margin-bottom: 1rem;">🚀 Get Started</h3>
            <p style="color: #f7fafc; margin-bottom: 1rem;">
                Use the sidebar to enter your User ID and get personalized movie recommendations using our two powerful algorithms:
            </p>
            <div style="text-align: left; margin: 1rem 0;">
                <p style="color: #f7fafc; margin: 0.5rem 0;">🎭 <strong>Content-Based Filtering</strong>: Recommendations based on movie genres and features</p>
                <p style="color: #f7fafc; margin: 0.5rem 0;">👥 <strong>Collaborative Filtering</strong>: Recommendations based on similar users' preferences</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)