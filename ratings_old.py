import requests
from tqdm import tqdm
import time
import pandas as pd
import os

# Sử dụng biến môi trường để bảo mật API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "69d161b64b2068d4396b3da0cc65e8f6")  # Khuyến nghị dùng .env


def get_trailer_url(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=15)

        # Xử lý lỗi API
        if response.status_code == 429:
            print("Đạt giới hạn request, đợi 10 giây...")
            time.sleep(10)
            return get_trailer_url(movie_id)  # Thử lại

        if response.status_code != 200:
            return None

        data = response.json()

        # Tìm trailer YouTube (ưu tiên chính thức trước)
        official_trailers = [v for v in data.get("results", [])
                             if v.get("type") == "Trailer"
                             and v.get("site") == "YouTube"
                             and v.get("official") is True]

        if official_trailers:
            return f"https://youtu.be/{official_trailers[0]['key']}"

        # Fallback: bất kỳ trailer nào
        unofficial = [v for v in data.get("results", [])
                      if v.get("type") == "Trailer"
                      and v.get("site") == "YouTube"]

        return f"https://youtu.be/{unofficial[0]['key']}" if unofficial else None

    except Exception as e:
        print(f"Lỗi với ID {movie_id}: {str(e)}")
        return None


# Đọc dữ liệu
print("Đang tải dataset...")
credit = pd.read_csv("credit.csv")

# Chỉ xử lý các bản ghi chưa có trailer (nếu chạy lại)
if "trailer_url" not in credit.columns:
    credit["trailer_url"] = None

# Lấy danh sách ID cần xử lý
to_process = credit[credit["trailer_url"].isnull()].index

print(f"Bắt đầu lấy trailer cho {len(to_process)} bộ phim...")
for idx in tqdm(to_process, total=len(to_process)):
    movie_id = credit.loc[idx, "movie_id"]
    credit.at[idx, "trailer_url"] = get_trailer_url(movie_id)

    # Điều chỉnh tốc độ theo giới hạn API
    time.sleep(0.3)  # ~33 requests/10s (< giới hạn 40)

# Lưu kết quả với timestamp
timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
credit.to_csv(f"credits{timestamp}.csv", index=False)
print("Hoàn thành! Dữ liệu đã được lưu.")
