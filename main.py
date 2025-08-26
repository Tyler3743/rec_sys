from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
app = FastAPI()
# Tạm thời đọc từ CSV; khi lên PostgreSQL, thay bằng truy vấn DB
movie = pd.read_csv('movies-new.csv')
movie = movie[movie['genres'] != '(no genres listed)']

def remove_imax(genres):
   return '|'.join([g for g in genres.split('|') if g != 'IMAX'])
movie['genres'] = movie['genres'].apply(remove_imax)
# Tính genre_list + vector
genre = set()
for i in movie['genres']:
   for j in i.split('|'):
       genre.add(j)
genre_list = sorted(genre)

def vector(genre, genre_list):
   return [1 if i in genre.split('|') else 0 for i in genre_list]
movie['genre_vector'] = movie['genres'].apply(lambda x: vector(x, genre_list))
ratings = pd.read_csv('ratings.csv')
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
   # Kiểm tra xem movie_id có tồn tại không
   if movie_id not in movies_df['movieId'].values:
       print(f"Không tìm thấy phim với movieId: {movie_id}")
       return None
   # Lấy genre vector của phim cần tìm
   target_movie = movies_df[movies_df['movieId'] == movie_id].iloc[0]
   target_vector = np.array(target_movie['genre_vector'])
   # Tính độ tương đồng với tất cả các phim khác
   similarities = []
   for idx, row in movies_df.iterrows():
       if row['movieId'] != movie_id:  # Loại bỏ chính phim đó
           movie_vector = np.array(row['genre_vector'])
           # Tính cosine similarity
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
   similarity_df = similarity_df.sort_values('similarity_score', ascending=False,ignore_index=True).head(top_n)
   return similarity_df

# Precompute user profiles khi server khởi động
print("🔄 Đang tính toán user profiles...")
user = ratings['userId'].unique()
user_profile_df = pd.DataFrame(index=user, columns=genre_list)
for uid in user:
   user_profile_df.loc[uid] = build_vector(uid, ratings, movie, genre_list).values
print(f"✅ Đã tính xong profiles cho {len(user)} users")


# Load thêm dữ liệu links và trailers
links = pd.read_csv('links.csv')
movie_trailers = pd.read_csv('movie-trailer.csv')


# Merge các bảng dữ liệu
movie = movie.merge(links[['movieId', 'tmdbId']], on='movieId', how='left')
movie = movie.merge(movie_trailers[['movieId', 'trailer_url']], on='movieId', how='left')

@app.get("/")
def home():
   return {
       "message": "Movie Recommendation API",
       "total_users": len(user_profile_df),
       "total_movies": len(movie),
       "movies_with_trailers": len(movie[movie['trailer_url'].notna()])
   }
@app.get("/recommendations")
def get_recommendations(user_id: int, top_n: int = 20):
   if user_id not in user_profile_df.index:
       raise HTTPException(status_code=404, detail=f"user_id {user_id} không tồn tại")
   recs = recommend(user_id, user_profile_df, movie, ratings, top_n)
   # Thêm trailer_url vào response
   return recs[['movieId', 'title', 'genres', 'tmdbId', 'trailer_url']].to_dict(orient='records')
@app.get("/users")
def get_users():
   return {"users": list(user_profile_df.index)}
@app.get("/similar_movies/{movie_id}")
def get_similar_movies(movie_id: int, top_n: int = 10):
   # Kiểm tra theo movieId (không phải tmdbId)
   if movie_id not in movie['movieId'].values:
       raise HTTPException(status_code=404, detail=f"Movie ID {movie_id} không tồn tại")
   # Get original movie data
   original_movie = movie[movie['movieId'] == movie_id].iloc[0].to_dict()

   # Get similar movies
   similar_movies_df = calculate_movie_similarity(movie_id, movie, top_n)
   if similar_movies_df is None:
       raise HTTPException(status_code=404, detail=f"Không thể tính toán phim tương tự cho ID {movie_id}")

   # Get full data for similar movies
   similar_movies = []
   for idx, row in similar_movies_df.iterrows():
       movie_data = movie[movie['movieId'] == row['movieId']].iloc[0]
       similar_movies.append({
           'movieId': int(row['movieId']),
           'title': row['title'],
           'genres': row['genres'],
           'similarity_score': float(row['similarity_score']),
           'tmdbId': int(movie_data['tmdbId']) if pd.notna(movie_data['tmdbId']) else None,
           'trailer_url': movie_data['trailer_url'] if pd.notna(movie_data['trailer_url']) else None
       })
   return {
       'original_movie': original_movie,
       'similar_movies': similar_movies
   }