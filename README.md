# 🎬 Movies.io - Movie Recommendation System

Hệ thống gợi ý phim dựa trên thuật toán Content-Based Filtering sử dụng FastAPI và Streamlit.

## 📋 Mô tả

Đây là một hệ thống recommendation system cho phim với:
- **Backend**: FastAPI với thuật toán content-based filtering
- **Frontend**: Streamlit với giao diện dark theme đẹp mắt
- **Dữ liệu**: MovieLens dataset (movies và ratings)

## 🚀 Cài đặt

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chuẩn bị dữ liệu
Đảm bảo có các file CSV trong thư mục:
- `movies-new.csv` - Thông tin phim
- `ratings.csv` - Đánh giá của user

## 🏃‍♂️ Chạy ứng dụng

### 1. Khởi động FastAPI Backend
```bash
uvicorn main:app --reload
```
- API sẽ chạy tại: http://localhost:8000
- Documentation: http://localhost:8000/docs

### 2. Khởi động Streamlit Frontend
```bash
streamlit run streamlit_with_api.py
```
- Frontend sẽ chạy tại: http://localhost:8501

## 📖 Cách sử dụng

### 1. FastAPI Endpoints
```bash
# Lấy recommendations cho user
GET /recommendations?user_id=1&top_n=10

# Ví dụ với curl
curl "http://localhost:8000/recommendations?user_id=1&top_n=5"
```

### 2. Streamlit Frontend
1. Mở browser tại http://localhost:8501
2. Nhập User ID trong sidebar
3. Chọn số lượng recommendations
4. Click "Get Recommendations"
5. Xem kết quả được hiển thị đẹp mắt

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    HTTP    ┌─────────────────┐
│   Streamlit     │ ────────── │     FastAPI     │
│   Frontend      │            │    Backend      │
└─────────────────┘            └─────────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   CSV Files     │
                              │ (movies, ratings)│
                              └─────────────────┘
```

## 🔧 Thuật toán

### Content-Based Filtering
1. **Genre Vectorization**: Chuyển đổi genres thành vector nhị phân
2. **User Profile**: Tính toán profile user dựa trên phim đã thích (rating >= 4)
3. **Similarity Calculation**: Tính độ tương đồng cosine giữa user profile và phim
4. **Recommendation**: Trả về top-N phim có độ tương đồng cao nhất

### Công thức tính toán
```
User Profile = Average(Genre Vectors của phim đã thích)
Similarity = Dot Product(User Profile, Movie Genre Vector)
```

## 📊 Dữ liệu

### Movies Dataset
- `movieId`: ID phim
- `title`: Tên phim
- `genres`: Thể loại (phân cách bằng |)

### Ratings Dataset
- `userId`: ID user
- `movieId`: ID phim
- `rating`: Đánh giá (1-5)
- `timestamp`: Thời gian đánh giá

## 🎨 Giao diện

### Features
- ✅ Dark theme đẹp mắt
- ✅ Responsive design
- ✅ Movie poster display
- ✅ Interactive buttons
- ✅ Real-time recommendations
- ✅ User-friendly interface

### Components
- Header với navigation
- Movie detail page
- Recommendation section
- Sidebar cho user input

## 🔮 Tính năng tương lai

- [ ] Collaborative Filtering
- [ ] Hybrid Recommendation
- [ ] PostgreSQL Database
- [ ] User Authentication
- [ ] Movie Rating System
- [ ] Advanced Search
- [ ] Movie Trailers
- [ ] Social Features

## 🛠️ Development

### Cấu trúc file
```
rec_sys/
├── main.py                 # FastAPI backend
├── streamlit_frontend.py   # Demo frontend
├── streamlit_with_api.py   # Frontend tích hợp API
├── requirements.txt        # Dependencies
├── README.md              # Documentation
├── movies-new.csv         # Movie data
└── ratings.csv            # Rating data
```

### API Documentation
Sau khi chạy FastAPI, truy cập:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 Lưu ý

1. **Performance**: Hệ thống precompute user profiles khi khởi động
2. **Memory**: Cần đủ RAM để load toàn bộ dataset
3. **Scalability**: Có thể cải thiện bằng database và caching

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

---

**Built with ❤️ using FastAPI and Streamlit**


