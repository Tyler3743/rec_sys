import pandas as pd
import numpy as np

# Load data
print("🔄 Loading data...")
movie = pd.read_csv('movies-new.csv')
movie = movie[movie['genres'] != '(no genres listed)']
ratings = pd.read_csv('ratings.csv')

# Preprocessing
def remove_imax(genres):
    return '|'.join([g for g in genres.split('|') if g != 'IMAX'])

movie['genres'] = movie['genres'].apply(remove_imax)

# Create genre list and vectors
genre = set()
for i in movie['genres']:
    for j in i.split('|'):
        genre.add(j)
genre_list = sorted(genre)

def vector(genre, genre_list):
    return [1 if i in genre.split('|') else 0 for i in genre_list]

movie['genre_vector'] = movie['genres'].apply(lambda x: vector(x, genre_list))

# Load additional data
links = pd.read_csv('links.csv')
movie_trailers = pd.read_csv('movie-trailer.csv')

# Merge additional data
movie = movie.merge(links[['movieId', 'tmdbId']], on='movieId', how='left')
movie = movie.merge(movie_trailers[['movieId', 'trailer_url']], on='movieId', how='left')

def build_vector(user_id, rating, movie, genre_list, threshold=4):
    like_movie = rating[(rating['userId'] == user_id) & (rating['rating'] >= threshold)]
    if like_movie.empty:
        return pd.Series(np.zeros(len(genre_list)), index=genre_list)
    like_genres = like_movie.merge(movie[['movieId', 'genre_vector']], on='movieId')
    if like_genres.empty:
        return pd.Series(np.zeros(len(genre_list)), index=genre_list)
    vectors = np.stack(like_genres['genre_vector'].to_list())
    cal = vectors.mean(axis=0)
    return pd.Series(cal, index=genre_list)

def recommend(user_id, user_profiles_df, movies_df, ratings_df, top_n=20):
    user_profile = user_profiles_df.loc[user_id]
    movie_vectors = np.stack(movies_df['genre_vector'].tolist())
    similarity_scores = movie_vectors.dot(user_profile.values)
    recommendations = movies_df.copy()
    recommendations['similarity_score'] = similarity_scores
    seen_movies = set(ratings_df[ratings_df['userId'] == user_id]['movieId'])
    recommendations = recommendations[~recommendations['movieId'].isin(seen_movies)]
    recommendations = recommendations.sort_values('similarity_score', ascending=False).head(top_n)
    return recommendations

def calculate_movie_similarity(movie_id, movies_df, top_n=10):
    # Check if movie_id exists
    if movie_id not in movies_df['movieId'].values:
        print(f"Không tìm thấy phim với movieId: {movie_id}")
        return None
    # Get genre vector of target movie
    target_movie = movies_df[movies_df['movieId'] == movie_id].iloc[0]
    target_vector = np.array(target_movie['genre_vector'])
    # Calculate similarity with all other movies
    similarities = []
    for idx, row in movies_df.iterrows():
        if row['movieId'] != movie_id:  # Exclude the movie itself
            movie_vector = np.array(row['genre_vector'])
            # Calculate cosine similarity
            dot_product = np.dot(target_vector, movie_vector)
            norm_target = np.linalg.norm(target_vector)
            norm_movie = np.linalg.norm(movie_vector)
            if norm_target > 0 and norm_movie > 0:
                similarity = dot_product / (norm_target * norm_movie)
            else:
                similarity = 0
            similarities.append({
                'movieId': row['movieId'],
                'title': row['title'],
                'genres': row['genres'],
                'similarity_score': similarity
            })
    similarity_df = pd.DataFrame(similarities)
    similarity_df = similarity_df.sort_values('similarity_score', ascending=False, ignore_index=True).head(top_n)
    return similarity_df

def show_similar_movies(movie_id, movies_df, top_n=10):
    """
    Hiển thị thông tin phim gốc và danh sách các phim tương tự
    """
    # Lấy thông tin phim gốc
    original_movie = movies_df[movies_df['movieId'] == movie_id]
    if original_movie.empty:
        print(f"Không tìm thấy phim với movieId: {movie_id}")
        return

    print("=" * 80)
    print("PHIM GỐC:")
    print(f"ID: {original_movie.iloc[0]['movieId']}")
    print(f"Tên: {original_movie.iloc[0]['title']}")
    print(f"Thể loại: {original_movie.iloc[0]['genres']}")
    print("=" * 80)

    # Tìm các phim tương tự
    similar_movies = calculate_movie_similarity(movie_id, movies_df, top_n)

    if similar_movies is not None:
        print(f"\nTOP {top_n} PHIM TƯƠNG TỰ:")
        print("-" * 80)

        for idx, row in similar_movies.iterrows():
            print(f"{idx + 1:2d}. {row['title']}")
            print(f"    ID: {row['movieId']} | Thể loại: {row['genres']}")
            print(f"    Độ tương đồng: {row['similarity_score']:.4f}")
            print()

# Precompute user profiles
print("🔄 Computing user profiles...")
user = ratings['userId'].unique()
user_profile_df = pd.DataFrame(index=user, columns=genre_list)
for uid in user:
    user_profile_df.loc[uid] = build_vector(uid, ratings, movie, genre_list).values
print(f"✅ Profiles computed for {len(user)} users")

# Test similar movies function with specific movie IDs
print("\n🔍 Testing similar movies functionality:")
test_movie_ids = [1, 2, 3]  # Replace with your desired movie IDs for testing
for movie_id in test_movie_ids:
    show_similar_movies(movie_id, movie)

# You can also add an interactive prompt to test with user input
while True:
    try:
        print("\n" + "=" * 80)
        print("Nhập ID phim để xem các phim tương tự (nhập 0 để thoát):")
        movie_id = int(input())
        if movie_id == 0:
            break
        show_similar_movies(movie_id, movie)
    except ValueError:
        print("ID phim không hợp lệ. Vui lòng nhập một số nguyên.")
    except Exception as e:
        print(f"Có lỗi xảy ra: {str(e)}")