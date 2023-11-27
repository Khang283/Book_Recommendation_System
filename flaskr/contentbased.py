import pandas as pd
import os

import re
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as npclea
from gensim.models.keyedvectors import KeyedVectors
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def joinPath(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", file_name)
    return file_path


books = pd.read_json(joinPath("metadata.json"), lines=True)
ratings = pd.read_json(joinPath("ratings.json"), lines=True)


def read_file_to_list(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
        return lines
    except FileNotFoundError:
        print(f"File not found at path: {file_path}")
        return []


stopwords_list = read_file_to_list(joinPath("stopwords.txt"))


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


books["preprocessed_description"] = books["description"].apply(data_preprocessing)

vectorizer = TfidfVectorizer()

tfidf_matrix = vectorizer.fit_transform(books["preprocessed_description"])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)


def get_movie(index):
    if index < len(books):
        return books.loc[index]
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
            {
                key: value
                for key, value in get_movie(index).to_dict().items()
                if key != "preprocessed_description"
            }
            for index in top_k_indices.index
        ]
    return recommended_films_list


class DocSim:
    def __init__(self, w2v_model):
        self.w2v_model = w2v_model

    def vectorize(self, doc: str, max_length: int = None) -> np.ndarray:
        words = [w for w in doc.split(" ")]
        word_vecs = []

        for word in words:
            try:
                vec = self.w2v_model[word]
                word_vecs.append(vec)
            except KeyError:
                pass

        if not word_vecs:
            return np.zeros(self.w2v_model.vector_size)

        vector = np.mean(word_vecs, axis=0)

        return vector

    def _cosine_sim(self, vecA, vecB):
        csim = np.dot(vecA, vecB) / (np.linalg.norm(vecA) * np.linalg.norm(vecB))
        if np.isnan(np.sum(csim)):
            return 0
        return csim

    def calculate_similarity(self, source_doc, target_docs=None, threshold=0):
        if not target_docs:
            return []

        if isinstance(target_docs, str):
            target_docs = [target_docs]

        max_length_source = max(
            len(self.vectorize(word)) for word in source_doc.split(" ")
        )
        max_length_target = max(
            len(self.vectorize(word)) for doc in target_docs for word in doc.split(" ")
        )
        max_length = max(max_length_source, max_length_target)

        source_vec = self.vectorize(source_doc, max_length)
        results = []
        for doc in target_docs:
            target_vec = self.vectorize(doc, max_length)
            sim_score = self._cosine_sim(source_vec, target_vec)
            if sim_score > threshold:
                results.append({"score": sim_score, "doc": doc})

        return results


googlenews_model_path = "GoogleNews-vectors-negative300.bin.gz"

model = KeyedVectors.load_word2vec_format(joinPath(googlenews_model_path), binary=True)


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def getTestAndTrain(userId, ratings, books):
    user_ratings = ratings[ratings["user_id"] == userId]
    if not user_ratings.empty:
        test_books = books[books["item_id"].isin(user_ratings["item_id"])]
        train_books = books[~books["item_id"].isin(user_ratings["item_id"])]
        return (test_books, train_books)
    return None


def calculate_cosine_similarity_books(test_books, train_books):
    ds = DocSim(model)

    test_description = test_books["preprocessed_description"].values[0]

    train_descriptions = train_books["preprocessed_description"].tolist()

    sim_scores = ds.calculate_similarity(test_description, train_descriptions)

    result = list(zip(train_books["item_id"], [score["score"] for score in sim_scores]))

    return result


def find_top_k_similar_books(userId, k, ratings, books):
    data = getTestAndTrain(userId, ratings, books)

    if data is not None:
        cosine_similarities = calculate_cosine_similarity_books(data[0], data[1])

        sorted_similarities = sorted(
            cosine_similarities, key=lambda x: x[1], reverse=True
        )

        top_k_cosine_similarities = sorted_similarities[:k]
        print(top_k_cosine_similarities)
        top_k_similar_id_books = [value[0] for value in top_k_cosine_similarities]

        top_k_similar_books = books[books["item_id"].isin(top_k_similar_id_books)]

        return top_k_similar_books
    return None


def recommended_k_films_user_id(userId, ratings, books):
    k = 5

    top_k_similar_books = find_top_k_similar_books(userId, k, ratings, books)

    if top_k_similar_books is not None:
        top_k_similar_books = top_k_similar_books.drop(
            columns=["preprocessed_description"]
        )
        recommended_films_list = top_k_similar_books.to_dict(orient="records")
        return recommended_films_list
    return []
