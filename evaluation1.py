import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split

# Load data (assuming movies-new.csv and ratings.csv are in the same directory)
movie = pd.read_csv('movies-new.csv')
movie = movie[movie['genres'] != '(no genres listed)']


def remove_imax(genres):
    return '|'.join([g for g in genres.split('|') if g != 'IMAX'])


movie['genres'] = movie['genres'].apply(remove_imax)

genre = set()
for i in movie['genres']:
    for j in i.split('|'):
        genre.add(j)
genre_list = sorted(genre)


def vector(genre, genre_list):
    return [1 if i in genre.split('|') else 0 for i in genre_list]


movie['genre_vector'] = movie['genres'].apply(lambda x: vector(x, genre_list))

ratings = pd.read_csv('ratings.csv')


def build_vector(user_id, rating_df, movie_df, genre_list, threshold=4):
    like_movie = rating_df[(rating_df['userId'] == user_id) & (rating_df['rating'] >= threshold)]
    if like_movie.empty:
        return pd.Series(np.zeros(len(genre_list)), index=genre_list)
    like_genres = like_movie.merge(movie_df[['movieId', 'genre_vector']], on='movieId')
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
    recommendations = recommendations.sort_values(by='similarity_score', ascending=False)
    return recommendations.head(top_n)


# --- Evaluation Metrics ---

def calculate_precision_recall(recommendations, actual_liked_movies, top_n):
    recommended_movie_ids = set(recommendations['movieId'].tolist())
    true_positives = len(recommended_movie_ids.intersection(actual_liked_movies))

    precision = true_positives / top_n if top_n > 0 else 0
    recall = true_positives / len(actual_liked_movies) if len(actual_liked_movies) > 0 else 0

    return precision, recall


def calculate_coverage(all_recommended_movies, all_movies):
    unique_recommended_movies = set(all_recommended_movies)
    coverage = len(unique_recommended_movies) / len(all_movies) if len(all_movies) > 0 else 0
    return coverage


# Main evaluation script
if __name__ == '__main__':
    # Split data for evaluation
    train_ratings, test_ratings = train_test_split(ratings, test_size=0.2, stratify=ratings['userId'], random_state=42)

    # Build user profiles on training data
    user_ids = train_ratings['userId'].unique()
    user_profiles = {}
    for user_id in user_ids:
        user_profiles[user_id] = build_vector(user_id, train_ratings, movie, genre_list)
    user_profiles_df = pd.DataFrame.from_dict(user_profiles, orient='index')

    all_precisions = []
    all_recalls = []
    all_recommended_movie_ids = set()
    inference_times = []
    top_n = 20  # Number of recommendations

    for user_id in user_ids:
        start_time = time.time()
        recommendations = recommend(user_id, user_profiles_df, movie, train_ratings, top_n=top_n)
        end_time = time.time()
        inference_times.append(end_time - start_time)

        actual_liked_movies = set(
            test_ratings[(test_ratings['userId'] == user_id) & (test_ratings['rating'] >= 4)]['movieId'].tolist())

        if not recommendations.empty and len(actual_liked_movies) > 0:
            precision, recall = calculate_precision_recall(recommendations, actual_liked_movies, top_n)
            all_precisions.append(precision)
            all_recalls.append(recall)

        all_recommended_movie_ids.update(recommendations['movieId'].tolist())

    avg_precision = np.mean(all_precisions) if all_precisions else 0
    avg_recall = np.mean(all_recalls) if all_recalls else 0
    avg_inference_time = np.mean(inference_times) if inference_times else 0

    total_movies = len(movie['movieId'].unique())
    coverage = calculate_coverage(all_recommended_movie_ids, movie['movieId'].unique())

    results = {
        'Average Precision': avg_precision,
        'Average Recall': avg_recall,
        'Coverage': coverage,
        'Average Inference Time (s)': avg_inference_time
    }

    results_df = pd.DataFrame([results])
    print(results_df)


