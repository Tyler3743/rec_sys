import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Dữ liệu Demo ---
# Trong một ứng dụng thực tế, bạn sẽ tải dữ liệu này từ một file CSV hoặc một cơ sở dữ liệu.
# Dữ liệu bao gồm: tiêu đề phim, thể loại, và link ảnh poster.
data = {
    'title': [
        'The Shawshank Redemption', 'The Godfather', 'The Dark Knight', 'Pulp Fiction',
        'Forrest Gump', 'Inception', 'The Matrix', 'Goodfellas',
        'Se7en', 'Interstellar'
    ],
    'genre': [
        'Drama, Crime', 'Crime, Drama', 'Action, Crime, Drama', 'Crime, Drama',
        'Drama, Romance', 'Action, Adventure, Sci-Fi', 'Action, Sci-Fi', 'Biography, Crime, Drama',
        'Crime, Drama, Mystery', 'Adventure, Drama, Sci-Fi'
    ],
    'poster_url': [
        'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
        'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
        'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
        'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',
        'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',
        'https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg',
        'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdU4SSTemYp.jpg',
        'https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkReEBdes.jpg',
        'https://image.tmdb.org/t/p/w500/6yoghtyTpznpBik8EngiMis2HG.jpg',
        'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg'
    ]
}
movies_df = pd.DataFrame(data)

# --- Xây dựng Mô hình Gợi ý ---
# Sử dụng TF-IDF để chuyển đổi văn bản thể loại thành vector số
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['genre'])

# Tính toán ma trận tương đồng cosine
# Ma trận này cho biết mức độ tương đồng giữa tất cả các cặp phim
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Tạo một series để map từ tiêu đề phim sang chỉ số (index)
indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()

def get_recommendations(title, cosine_sim=cosine_sim):
    """
    Hàm này nhận vào tiêu đề phim và trả về danh sách các phim được gợi ý.
    """
    # Lấy chỉ số của phim được chọn
    idx = indices[title]

    # Lấy điểm tương đồng của tất cả các phim với phim được chọn
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sắp xếp các phim dựa trên điểm tương đồng (từ cao đến thấp)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Lấy 5 phim có điểm tương đồng cao nhất (bỏ qua phim đầu tiên vì đó là chính nó)
    sim_scores = sim_scores[1:6]

    # Lấy chỉ số của các phim được gợi ý
    movie_indices = [i[0] for i in sim_scores]

    # Trả về thông tin của các phim được gợi ý
    return movies_df.iloc[movie_indices]

# --- Giao diện người dùng (UI) với Streamlit ---

# Cấu hình trang web
st.set_page_config(layout="wide", page_title="Hệ thống Gợi ý Phim")

# Thêm CSS tùy chỉnh để giao diện đẹp hơn
st.markdown("""
<style>
    /* Thay đổi font chữ của toàn bộ ứng dụng */
    .stApp {
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Tiêu đề chính */
    .title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF4B4B;
        padding: 20px;
    }
    /* Tiêu đề phụ */
    .subtitle {
        font-size: 1.5rem;
        text-align: center;
        color: #E0E0E0;
    }
    /* Style cho các thẻ phim */
    .movie-card {
        background-color: #222222;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        height: 100%; /* Đảm bảo các card có cùng chiều cao */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .movie-card:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.5);
        transform: scale(1.03); /* Hiệu ứng phóng to khi di chuột qua */
    }
    .movie-poster {
        width: 100%;
        border-radius: 7px;
    }
    .movie-title {
        font-size: 1rem;
        font-weight: bold;
        color: #FFFFFF;
        margin-top: 10px;
    }
    .movie-genre {
        font-size: 0.8rem;
        color: #B0B0B0;
    }
</style>
""", unsafe_allow_html=True)

# --- Phần đầu trang ---
st.markdown('<p class="title">🎬 Hệ thống Gợi ý Phim</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Chọn một bộ phim bạn yêu thích để nhận gợi ý!</p>', unsafe_allow_html=True)
st.write("") # Thêm khoảng trống

# --- Thanh lựa chọn phim ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_movie_title = st.selectbox(
        'Chọn hoặc tìm kiếm một bộ phim:',
        movies_df['title'].values
    )

st.write("---") # Đường kẻ ngang phân cách

# --- Hiển thị kết quả ---
if selected_movie_title:
    # Lấy danh sách phim được gợi ý
    recommendations = get_recommendations(selected_movie_title)

    # Hiển thị phim đã chọn
    st.header(f"Vì bạn đã xem '{selected_movie_title}', chúng tôi gợi ý:")
    st.write("")

    # Sử dụng st.columns để hiển thị các phim gợi ý theo hàng ngang
    cols = st.columns(len(recommendations))
    for i, (idx, row) in enumerate(recommendations.iterrows()):
        with cols[i]:
            st.markdown(
                f"""
                <div class="movie-card">
                    <img src="{row['poster_url']}" class="movie-poster">
                    <div>
                        <p class="movie-title">{row['title']}</p>
                        <p class="movie-genre">{row['genre']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# --- Chân trang ---
st.write("---")
st.markdown("<div style='text-align: center; color: grey;'>Xây dựng với ❤️ bằng Streamlit</div>", unsafe_allow_html=True)

