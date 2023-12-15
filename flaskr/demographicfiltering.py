import pandas as pd
import os


def joinPath(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", file_name)
    return file_path


# books = pd.read_json(joinPath("metadata.json"), lines=True)
# ratings = pd.read_json(joinPath("ratings.json"), lines=True)
books = pd.read_json("./data/rawdata/metadata.json", lines=True)
ratings = pd.read_json("./data/rawdata/ratings.json", lines=True)

grouped_ratings = ratings.groupby("item_id")

# Tính vote_average và vote_count
vote_average = grouped_ratings["rating"].mean()
vote_count = grouped_ratings["rating"].count()

# Tạo DataFrame mới từ kết quả
result_df = pd.DataFrame(
    {
        "item_id": vote_average.index,
        "vote_average": vote_average.values,
        "vote_count": vote_count.values,
    }
)

df = pd.merge(books, result_df, on="item_id", how="left")

C = df["vote_average"].mean()

m = df["vote_count"].quantile(0.9)

q_movies = df.copy().loc[df["vote_count"] >= m]


def weighted_rating(x, m=m, C=C):
    v = x["vote_count"]
    R = x["vote_average"]
    # Calculation based on the IMDB formula
    return (v / (v + m) * R) + (m / (m + v) * C)


def recommended(k):
    q_movies = df.copy().loc[df["vote_count"] >= m]
    q_movies["score"] = q_movies.apply(weighted_rating, axis=1)
    q_movies = q_movies.sort_values("score", ascending=False)
    result = (
        q_movies.head(k)
        .drop(["vote_average", "vote_count", "score"], axis=1)
        .to_dict(orient="records")
    )

    return result
