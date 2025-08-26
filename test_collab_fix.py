import requests
import pandas as pd

# Test collaborative filtering API
def test_collab_api():
    print("Testing Collaborative Filtering API...")
    
    # Test với user_id = 1
    user_id = 1
    top_n = 5
    
    try:
        response = requests.get(f"http://localhost:8001/recommendations1?user_id={user_id}&top_n={top_n}")
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Success! Found {len(recommendations)} recommendations")
            
            # Kiểm tra cấu trúc dữ liệu
            if recommendations:
                first_movie = recommendations[0]
                print(f"\nFirst movie structure:")
                print(f"movieId: {first_movie.get('movieId')}")
                print(f"title: {first_movie.get('title')}")
                print(f"tmdbId: {first_movie.get('tmdbId')}")
                print(f"genres: {first_movie.get('genres')}")
                
                # Test TMDB API call
                tmdb_id = first_movie.get('tmdbId')
                if tmdb_id and pd.notna(tmdb_id):
                    print(f"\nTesting TMDB API with tmdbId: {tmdb_id}")
                    tmdb_url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}"
                    tmdb_params = {
                        'api_key': '37aa7e398fc505cdf4169bded99efe8c',
                        'language': 'en-US'
                    }
                    tmdb_response = requests.get(tmdb_url, params=tmdb_params)
                    
                    if tmdb_response.status_code == 200:
                        movie_data = tmdb_response.json()
                        print(f"✅ TMDB API success!")
                        print(f"Title: {movie_data.get('title')}")
                        print(f"Overview: {movie_data.get('overview', 'No overview')[:100]}...")
                    else:
                        print(f"❌ TMDB API failed with status: {tmdb_response.status_code}")
                else:
                    print(f"❌ No valid tmdbId found: {tmdb_id}")
            else:
                print("❌ No recommendations returned")
        else:
            print(f"❌ API failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Collaborative Filtering API server")
        print("Make sure to run: uvicorn main2:app --reload --port 8001")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_collab_api()
