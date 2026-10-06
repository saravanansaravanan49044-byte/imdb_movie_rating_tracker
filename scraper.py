import pandas as pd

BASICS_URL = "https://datasets.imdbws.com/title.basics.tsv.gz"
RATINGS_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"

print("Downloading IMDb ratings...")

# Ratings file is much smaller
ratings = pd.read_csv(
    RATINGS_URL,
    sep="\t",
    compression="gzip"
)

# Keep only movies with ratings
print("Downloading movie details...")

movie_parts = []

for chunk in pd.read_csv(
    BASICS_URL,
    sep="\t",
    compression="gzip",
    chunksize=50000,
    low_memory=False
):
    # Only movies
    chunk = chunk[chunk["titleType"] == "movie"]

    # Keep only required columns
    chunk = chunk[
        ["tconst", "primaryTitle", "startYear"]
    ]

    movie_parts.append(chunk)

    print("Processed:", sum(len(x) for x in movie_parts), "movies")

movies = pd.concat(movie_parts, ignore_index=True)

# Combine ratings with movie details
data = movies.merge(
    ratings,
    on="tconst",
    how="inner"
)

# Remove missing values
data = data.dropna(
    subset=[
        "primaryTitle",
        "startYear",
        "averageRating",
        "numVotes"
    ]
)

# Convert values
data["startYear"] = pd.to_numeric(
    data["startYear"],
    errors="coerce"
)

data["averageRating"] = pd.to_numeric(
    data["averageRating"],
    errors="coerce"
)

data["numVotes"] = pd.to_numeric(
    data["numVotes"],
    errors="coerce"
)

data = data.dropna()

# Sort by rating and votes
data = data.sort_values(
    ["averageRating", "numVotes"],
    ascending=[False, False]
)

# Select 250 movies
top250 = data.head(250).copy()

# Add rank
top250.insert(
    0,
    "Rank",
    range(1, len(top250) + 1)
)

# Select final columns
output = top250[
    [
        "Rank",
        "primaryTitle",
        "startYear",
        "averageRating",
        "numVotes"
    ]
]

# Rename columns
output.columns = [
    "Rank",
    "Movie_Name",
    "Year",
    "Rating",
    "Votes"
]

# Save CSV
output.to_csv(
    "imdb_250_movies.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n================================")
print("SUCCESS!")
print("================================")
print("250 movie CSV created!")
print("File: imdb_250_movies.csv")
print("Total movies:", len(output))