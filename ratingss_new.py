import requests
from tqdm import tqdm
import time
import pandas as pd
import os

# Sử dụng biến môi trường để bảo mật API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "69d161b64b2068d4396b3da0cc65e8f6")  # Khuyến nghị dùng .env


def get_trailer_url(tmdbId):
    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdbId}/videos?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=15)

        # Xử lý lỗi API
        if response.status_code == 429:
            print("Đạt giới hạn request, đợi 10 giây...")
            time.sleep(10)
            return get_trailer_url(tmdbId)  # Thử lại

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
        print(f"Lỗi với ID {tmdbId}: {str(e)}")
        return None


# Đọc dữ liệu
print("Đang tải dataset...")
movies_new = pd.read_csv("movie_trailer_temp.csv")

# Chỉ xử lý các bản ghi chưa có trailer (nếu chạy lại)
if "trailer_url" not in movies_new.columns:
    movies_new["trailer_url"] = None

# Lấy danh sách ID cần xử lý
to_process = movies_new[movies_new["trailer_url"].isnull()].index

print(f"Bắt đầu lấy trailer cho {len(to_process)} bộ phim...")
for idx in tqdm(to_process, total=len(to_process)):
    tmdbId = movies_new.loc[idx, "tmdbId"]
    movies_new.at[idx, "trailer_url"] = get_trailer_url(tmdbId)

    # Điều chỉnh tốc độ theo giới hạn API
    time.sleep(0.3)  # ~33 requests/10s (< giới hạn 40)

    # Lưu file tạm sau mỗi lần xử lý phim
    movies_new.to_csv("movie_trailer_temp.csv", index=False)

# Lưu kết quả với timestamp
timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
movies_new.to_csv(f"movie_trailer{timestamp}.csv", index=False)
print("Hoàn thành! Dữ liệu đã được lưu.")
trailer_list = movies_new[movies_new["trailer_url"].notnull()][["movieId", "tmdbId", "trailer_url"]]
print(trailer_list.to_string(index=False))
print(movies_new['trailer_url'].notnull().sum())