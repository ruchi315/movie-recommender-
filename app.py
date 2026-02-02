from flask import Flask, render_template, request
import pickle
import pandas as pd
import os
import gdown  # Handles large Google Drive downloads
import requests  # For TMDb API

app = Flask(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths for local files
movies_path = os.path.join(BASE_DIR, "movies.pkl")
similarity_path = os.path.join(BASE_DIR, "similarity.pkl")

# Google Drive download URL (large file)
SIMILARITY_URL = "https://drive.google.com/uc?id=14qwXpydzboCnzRG_jLtlW2xjLQP87eYS"

# Download similarity.pkl if not present
if not os.path.exists(similarity_path):
    gdown.download(SIMILARITY_URL, similarity_path, quiet=False)

# Load data
movies = pickle.load(open(movies_path, "rb"))
similarity = pickle.load(open(similarity_path, "rb"))

# TMDb API key
TMDB_API_KEY = "bb534df606f2cd2be7ff131da8b14a93"

# Function to fetch poster URL from TMDb
def get_poster_url(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        results = data.get("results")
        if results and results[0].get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + results[0]["poster_path"]
    except Exception:
        pass
    return ""  # fallback if poster not found

# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []
    for i in movie_list:
        title = movies.iloc[i[0]].title
        poster = get_poster_url(title)
        recommendations.append({"title": title, "poster": poster})

    return recommendations

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    selected_movie = None
    if request.method == "POST":
        selected_movie = request.form.get("movie")
        if selected_movie:
            recommendations = recommend(selected_movie)

    return render_template(
        "index.html",
        movies=movies['title'].values,
        recommendations=recommendations,
        selected_movie=selected_movie
    )

# Run app locally
if __name__ == "__main__":
    app.run(debug=True)
