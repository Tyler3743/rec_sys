import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity

# Load data
ratings = pd.read_csv("ratings.csv")
movie = pd.read_csv("movies-new.csv")


def collaborative_filtering_recommend(user_id, ratings_df, movies_df, top_n):
    """User-based Collaborative Filtering"""
    # Tạo ma trận người dùng - sản phẩm
    user_item_matrix = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)

    # Kiểm tra xem user_id có trong ma trận không
    if user_id not in user_item_matrix.index:
        return []  # Trả về danh sách rỗng nếu không tìm thấy người dùng

    # Tính toán độ tương đồng giữa các người dùng
    user_similarity = cosine_similarity(user_item_matrix)
    user_idx = user_item_matrix.index.get_loc(user_id)

    # Lấy 10 người dùng tương đồng nhất
    similar_users = user_similarity[user_idx].argsort()[::-1][1:11]

    predictions = []
    # Dự đoán điểm đánh giá cho các phim
    for movie_id in movies_df['movieId']:
        if movie_id in user_item_matrix.columns:
            similar_ratings = []
            similar_weights = []
            for similar_user_idx in similar_users:
                similar_user_id = user_item_matrix.index[similar_user_idx]
                rating = user_item_matrix.loc[similar_user_id, movie_id]
                if rating > 0:
                    similarity = user_similarity[user_idx, similar_user_idx]
                    similar_ratings.append(rating * similarity)
                    similar_weights.append(similarity)

            if similar_weights:
                predicted_rating = sum(similar_ratings) / sum(similar_weights)
                predictions.append((movie_id, predicted_rating))

    # Sắp xếp các dự đoán
    predictions.sort(key=lambda x: x[1], reverse=True)
    return [movie_id for movie_id, _ in predictions[:top_n]]


# --- Evaluation Metrics ---

def calculate_precision_recall(recommendations, actual_liked_movies, top_n):
    recommended_movie_ids = set(recommendations)
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

    user_ids = test_ratings['userId'].unique()

    all_precisions = []
    all_recalls = []
    all_recommended_movie_ids = set()
    inference_times = []
    top_n = 20  # Number of recommendations

    for user_id in user_ids:
        start_time = time.time()
        recommendations = collaborative_filtering_recommend(user_id, train_ratings, movie, top_n=top_n)
        end_time = time.time()
        inference_times.append(end_time - start_time)

        actual_liked_movies = set(
            test_ratings[(test_ratings['userId'] == user_id) & (test_ratings['rating'] >= 4)]['movieId'].tolist())

        if recommendations and len(actual_liked_movies) > 0:
            precision, recall = calculate_precision_recall(recommendations, actual_liked_movies, top_n)
            all_precisions.append(precision)
            all_recalls.append(recall)

        all_recommended_movie_ids.update(recommendations)

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
    # results_df.to_csv('evaluation_collab_results.csv', index=False)
    # print('Evaluation results saved to evaluation_collab_results.csv')
    print(results_df)


