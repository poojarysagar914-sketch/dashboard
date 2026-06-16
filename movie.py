import os
import pandas as pd
import requests

# Example using TMDB API (You'll need a free API key from their site)
API_KEY = os.environ.get("TMDB_API_KEY")
if not API_KEY:
    raise ValueError("Please set the TMDB_API_KEY environment variable before running the script.")

URL = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1"

response = requests.get(URL).json()
movies_list = []

for movie in response["results"]:
    movies_list.append(
        {
            "movie_id": movie["id"],
            "title": movie["title"],
            "release_date": movie["release_date"],
            "vote_average": movie["vote_average"],
            "popularity": movie["popularity"],
        }
    )

# Convert to a clean Pandas DataFrame
df = pd.DataFrame(movies_list)

# Quick Data Cleaning
df["release_date"] = pd.to_datetime(df["release_date"])
df.dropna(inplace=True)
