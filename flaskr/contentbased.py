import pandas as pd
import os

import re
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from gensim.models.keyedvectors import KeyedVectors
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk

print("CB")
nltk.download('punkt')
# Kiểm tra xem mô-đun punkt đã được tải hay chưa
# if not nltk.data.find('tokenizers/punkt'):
#     nltk.download('punkt')
# else:
#     print("Mô-đun punkt đã được tải.")

def joinPath(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "", file_name)
    return file_path

books = pd.read_json("./data/rawdata/metadata.json", lines=True)
ratings = pd.read_json("./data/rawdata/ratings.json", lines=True)

# books = pd.read_json(joinPath("..\data\rawdata\metadata.json"), lines=True)
# ratings = pd.read_json(joinPath("data\rawdata\ratings.json"), lines=True)

# Lọc theo user_id có ít nhất n lần rating
n = 300
user_counts = ratings["user_id"].value_counts()
valid_users = user_counts[user_counts >= n].index
filtered_ratings_by_user = ratings[ratings["user_id"].isin(valid_users)]

# Lọc theo item_id có ít nhất m lần rating
m = 10
item_counts = ratings["item_id"].value_counts()
valid_items = item_counts[item_counts >= m].index
filtered_ratings = filtered_ratings_by_user[
    filtered_ratings_by_user["item_id"].isin(valid_items)
]


def read_file_to_list(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
        return lines
    except FileNotFoundError:
        print(f"File not found at path: {file_path}")
        return []


# stopwords_list = read_file_to_list(joinPath("stopwords.txt"))
stopwords_list = read_file_to_list("./data/W2v/stopwords.txt")

def remove_punctuation(text):
    if isinstance(text, str):
        text = re.sub(r"[^\w\s]", "", text)
    return text


def remove_stopwords(text):
    if isinstance(text, str):
        words = text.split(" ")
        filtered_words = [word for word in words if word not in stopwords_list]
        return " ".join(filtered_words)
    return text


def tokenize_text(text):
    if isinstance(text, str):
        tokens = word_tokenize(text)
        return " ".join(tokens)
    return ""


def data_preprocessing(description):
    if isinstance(description, str):
        description = description.lower()
        description = remove_punctuation(description)
        description = remove_stopwords(description)
        return tokenize_text(description)
    return ""


books["preprocessed_description"] = books.apply(
    lambda row: " ".join(
        [
            str(row["title"]),
            str(row["authors"]),
            str(row["year"]),
            str(row["description"]),
        ]
    ),
    axis=1,
)
books["preprocessed_description"] = books["preprocessed_description"].apply(
    data_preprocessing
)


def getTestAndTrain(userId, ratings, books):
    user_ratings = ratings[ratings["user_id"] == userId]
    if not user_ratings.empty:
        test_books = books[books["item_id"].isin(user_ratings["item_id"])]
        train_books = books[~books["item_id"].isin(user_ratings["item_id"])]
        return (test_books, train_books)
    return (None, None)


vectorizer = TfidfVectorizer()

tfidf_matrix = vectorizer.fit_transform(books["preprocessed_description"])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)


def get_movie(id):
    if len(books[books["item_id"] == id]) != 0:
        return books[books["item_id"] == id]["title"].values[0]
    else:
        return "Không tìm thấy bộ phim"


def get_movie_index(movie_name):
    book = books[books["title"] == movie_name]
    if len(book) != 0:
        return book.index[0]
    else:
        return -1


def recommended_k_films_by_movie_name(movie_name):
    k = 10
    index = get_movie_index(movie_name)
    if index != -1:
        df = pd.DataFrame({"cosine": cosine_sim[index]})
        df = df.drop(index=index)
        top_k_indices = df["cosine"].nlargest(k)
        recommended_films_list = [
            books.loc[index].to_dict() for index in top_k_indices.index
        ]
    return recommended_films_list


googlenews_model_path = "./data/W2v/GoogleNews-vectors-negative300.bin.gz"

model = KeyedVectors.load_word2vec_format(googlenews_model_path, binary=True)


def vectorize(doc: str, w2v_model) -> np.ndarray:
    words = [w for w in doc.split(" ")]
    word_vecs = []

    for word in words:
        try:
            vec = w2v_model[word]
            word_vecs.append(vec)
        except KeyError:
            pass

    if not word_vecs:
        return np.zeros(w2v_model.vector_size)

    vector = np.mean(word_vecs, axis=0)

    return vector


def _cosine_sim(vecA, vecB):
    # Calculate the dot product of vecA and vecB
    dot_product = np.dot(vecA, vecB)

    # Calculate the magnitudes of vecA and vecB
    magnitude_A = np.linalg.norm(vecA)
    magnitude_B = np.linalg.norm(vecB)

    # Calculate the cosine similarity
    if magnitude_A != 0 and magnitude_B != 0:
        cosine_similarity = dot_product / (magnitude_A * magnitude_B)
    else:
        cosine_similarity = 0  # Default value if one of the vectors has zero magnitude

    return cosine_similarity


def calculate_cosine_similarity_books_w2v(test_books, train_books, model=model):
    test = "".join(test_books["preprocessed_description"].values)
    train = train_books["preprocessed_description"].values

    test_vec = vectorize(test, model)

    train_vecs = [vectorize(data, model) for data in train]

    sim_scores = [_cosine_sim(test_vec, vec) for vec in train_vecs]

    return sim_scores


def find_top_k_similar_books_w2v(userId, k, ratings=filtered_ratings):
    test_books, train_books = getTestAndTrain(userId, ratings, books)

    if test_books is not None:
        cosine_similarities = calculate_cosine_similarity_books_w2v(
            test_books, train_books
        )

        cos_df = train_books.copy()

        cos_df["cos_sim"] = cosine_similarities

        top_k_similar_books = cos_df.sort_values(by="cos_sim", ascending=False).head(k)

        return top_k_similar_books
    return None


def w2v_recommendation(userId, k, ratings=filtered_ratings):
    top_k_similar_books = find_top_k_similar_books_w2v(userId, k, ratings)
    if top_k_similar_books is not None:
        return top_k_similar_books.drop("cos_sim", axis=1).to_dict(orient="records")


def w2v_recommendation_df(userId, k, ratings=filtered_ratings):
    top_k_similar_books = find_top_k_similar_books_w2v(userId, k, ratings)
    if top_k_similar_books is not None:
        return top_k_similar_books
