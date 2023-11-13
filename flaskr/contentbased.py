import os
import json
import re
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt")


def getData(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", file_name)
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


books = getData("metadata.json")
ratings = getData("ratings.json")


def read_file_to_list(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
        return lines
    except FileNotFoundError:
        print(f"File not found at path: {file_path}")
        return []


stopwords_list = read_file_to_list("stopwords.txt")


def removePunctuation(text):
    if isinstance(text, str):
        text = re.sub(r"[^\w\s]", "", text)
    return text


def removeStopwords(text):
    if isinstance(text, str):
        words = text.split(" ")
        filtered_words = [word for word in words if word not in stopwords_list]
        return " ".join(filtered_words)
    return text


def tokenizeText(text):
    if isinstance(text, str):
        tokens = word_tokenize(text)
        return " ".join(tokens)
    return text


def dataPreprocessing():
    for book in books:
        if isinstance(book["description"], str):
            book["description"] = book["description"].lower()
            book["description"] = removePunctuation(book["description"])
            book["description"] = removeStopwords(book["description"])
            book["description"] = tokenizeText(book["description"])
        else:
            book["description"] = ""


dataPreprocessing()


def getTestAndTrain(userId):
    item_ids = [rating["item_id"] for rating in ratings if rating["user_id"] == userId]
    if len(item_ids) != 0:
        test_books = [book for book in books if book["item_id"] in item_ids]
        train_books = [book for book in books if book["item_id"] not in item_ids]
        return (test_books, train_books)
    return None


def calculate_cosine_similarity_books(test_books, train_books):
    test = " ".join([book["description"] for book in test_books])

    data = [test] + [book["description"] for book in train_books]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(data)
    cosine_similarities = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]

    result = [
        (book["item_id"], cosine_similarities[i]) for i, book in enumerate(train_books)
    ]

    return result


def find_top_k_similar_books(userId, k):
    data = getTestAndTrain(userId)

    if data is not None:
        cosine_similarities = calculate_cosine_similarity_books(data[0], data[1])

        sorted_similarities = sorted(
            cosine_similarities, key=lambda x: x[1], reverse=True
        )

        top_k_cosine_similarities = sorted_similarities[:k]
        print(top_k_cosine_similarities)
        top_k_similar_id_books = [value[0] for value in top_k_cosine_similarities]

        top_k_similar_books = [
            book for book in books if book["item_id"] in top_k_similar_id_books
        ]

        return top_k_similar_books
    return None


def contentbasedRecommendationSystem(userId):
    k = 5

    top_k_similar_books = find_top_k_similar_books(userId, k)
    if top_k_similar_books is not None:
        return top_k_similar_books
