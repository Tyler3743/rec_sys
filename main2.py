from fastapi import FastAPI, HTTPException
import pandas as pd
from collab import collaborative_filtering_recommend
import numpy as np
# Tải dữ liệu một lần khi ứng dụng khởi động
ratings = pd.read_csv('ratings.csv')
links = pd.read_csv('links.csv')
movie_info = pd.read_csv('movies-new.csv')

# Merge thông tin phim với trailer để có đầy đủ thông tin
movies = links.merge(movie_info, on='movieId', how='left')

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Movie Recommendation API",
        "total_users": len(ratings['userId'].unique()),
        "total_movies": len(movies),
        "movies_with_trailers": len(movies[movies['trailer_url'].notna()])
    }


@app.get("/recommendations1")
def get_recommendations(user_id: int, top_n: int = 20):
    if user_id not in ratings['userId'].unique():
        raise HTTPException(status_code=404, detail=f"user_id {user_id} không tồn tại")

    # Lấy danh sách ID phim được gợi ý
    recs_ids = collaborative_filtering_recommend(user_id, ratings, movies, top_n)

    # Lấy thông tin chi tiết của các phim được gợi ý
    recommended_movies = movies[movies['movieId'].isin(recs_ids)]

    # Trả về kết quả dưới dạng dictionary
    return recommended_movies.to_dict(orient='records')

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
@app.get("/similar_movies/{movie_id}")
def get_similar_movies(movie_id: int, top_n: int = 10):
   # Kiểm tra theo movieId (không phải tmdbId)
   if movie_id not in movies['movieId'].values:
       raise HTTPException(status_code=404, detail=f"Movie ID {movie_id} không tồn tại")
   # Get original movie data
   original_movie = movies[movies['movieId'] == movie_id].iloc[0].to_dict()

   # Get similar movies
   similar_movies_df = calculate_movie_similarity(movie_id, movies, top_n)
   if similar_movies_df is None:
       raise HTTPException(status_code=404, detail=f"Không thể tính toán phim tương tự cho ID {movie_id}")

   # Get full data for similar movies
   similar_movies = []
   for idx, row in similar_movies_df.iterrows():
       movie_data = movies[movies['movieId'] == row['movieId']].iloc[0]
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