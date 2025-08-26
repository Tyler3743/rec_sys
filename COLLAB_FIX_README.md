# Sửa lỗi Collaborative Filtering với TMDB API

## Vấn đề
Khi sử dụng Collaborative Filtering, chương trình bị lỗi khi lấy thông tin phim từ TMDB API vì:
1. File `movies-new.csv` không có cột `tmdbId`
2. Không có xử lý fallback khi `tmdbId` không hợp lệ hoặc không tồn tại

## Giải pháp đã thực hiện

### 1. Cập nhật `main2.py`
- Thay đổi từ sử dụng `movies-new.csv` sang `movie-trailer.csv` (có cột `tmdbId`)
- Merge với `movies-new.csv` để có đầy đủ thông tin (title, genres)
- Code thay đổi:
```python
# Trước
movies = pd.read_csv('movies-new.csv')

# Sau
movie_trailers = pd.read_csv('movie-trailer.csv')
movie_info = pd.read_csv('movies-new.csv')
movies = movie_trailers.merge(movie_info, on='movieId', how='left')
```

### 2. Cải thiện xử lý lỗi trong `frontend.py`

#### a) Hàm `get_movie_details()`
- Thêm kiểm tra `tmdb_id` hợp lệ trước khi gọi API
- Thêm try-catch cho việc chuyển đổi `tmdb_id` thành int
- Code thay đổi:
```python
if tmdb_id is not None and pd.notna(tmdb_id) and str(tmdb_id).strip() != '':
    try:
        detail_url = f"{TMDB_BASE_URL}/movie/{int(tmdb_id)}"
        # ... API call
    except (ValueError, TypeError):
        # Fallback to title search
        pass
```

#### b) Hàm `get_movie_trailer_from_tmdb()`
- Thêm kiểm tra `tmdb_id` hợp lệ
- Thêm try-catch cho việc chuyển đổi `tmdb_id` thành int

#### c) Thêm fallback cho hiển thị phim
- Khi không lấy được thông tin từ TMDB API, sử dụng dữ liệu local
- Áp dụng cho:
  - Hiển thị phim chính trong recommendations
  - Hiển thị phim trong danh sách recommendations
  - Hiển thị phim trong similar movies

### 3. Xử lý dữ liệu genres
- Thêm kiểm tra `pd.notna()` cho trường `genres` để tránh lỗi khi genres là NaN
- Code thay đổi:
```python
'genres': movie.get('genres', '').split('|') if movie.get('genres') and pd.notna(movie.get('genres')) else []
```

## Cách test

### 1. Chạy API servers
```bash
# Terminal 1 - Content-based API
uvicorn main:app --reload

# Terminal 2 - Collaborative Filtering API  
uvicorn main2:app --reload --port 8001
```

### 2. Test với script
```bash
python test_collab_fix.py
```

### 3. Test với Streamlit
```bash
streamlit run frontend.py
```

## Kết quả mong đợi
- Collaborative Filtering sẽ hoạt động bình thường
- Thông tin phim sẽ được hiển thị ngay cả khi không lấy được từ TMDB API
- Không còn lỗi khi `tmdbId` không hợp lệ hoặc không tồn tại
- Fallback gracefully về dữ liệu local khi cần thiết
