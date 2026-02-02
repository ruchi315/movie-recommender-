from flask import Flask, render_template, request
import pickle
import os
import gdown  # Handles large Google Drive downloads

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
    print("Downloading similarity.pkl from Google Drive...")
    gdown.download(SIMILARITY_URL, similarity_path, quiet=False)
    print("Download complete!")

# Load data
movies = pickle.load(open(movies_path, "rb"))
similarity = pickle.load(open(similarity_path, "rb"))

# Recommendation function (titles only)
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    # Return only titles
    return [movies.iloc[i[0]].title for i in movie_list]

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    if request.method == "POST":
        movie = request.form.get("movie")
        if movie:
            recommendations = recommend(movie)

    return render_template(
        "index.html",
        movies=movies['title'].values,
        recommendations=recommendations
    )

if __name__ == "__main__":
    app.run(debug=True)
