from sklearn.metrics.pairwise import cosine_similarity
# import pandas as pd
# import numpy as np
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

    # Lọc ra các phim người dùng đã xem
    watched_movies = set(ratings_df[ratings_df['userId'] == user_id]['movieId'])

    recommendations = []
    for movie_id, predicted_rating in predictions:
        if movie_id not in watched_movies:
            recommendations.append(movie_id)
        if len(recommendations) >= top_n:
            break
    return recommendations

