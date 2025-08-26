import pandas as pd
import numpy as np
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
   return recommendations