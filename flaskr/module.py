import json
import random
import pandas as pd
from werkzeug.exceptions import abort
from flaskr import CFService
from pathlib import Path
from flaskr import contentbased as CB
from flaskr import demographicfiltering as DF
from flaskr import hybrid

print("module")
pathKNN = Path('./data/knn_prediction.csv')
pathALS = Path('./data/als_prediction.csv')
service = CFService.CFService(pathKNN, pathALS)

def getList(url):
    # data=[]
    # with open(url, 'r') as f:
    #     for line in f:
    #             data.append(json.loads(line))
    print(url)
    # data = pd.read_csv(url)
    data = pd.read_json(url, lines=True)
    # data = data.to_dict(orient='records')
    return data

def getRatingavg(book_id, ratings):
    rating_movie = ratings[ratings["item_id"] == int(book_id)]
    average_rating = rating_movie["rating"].mean()

    return round(average_rating, 2)

def getRatingBookByUser(book_id, user_id, ratings):
    rating = ratings[(ratings["item_id"] == book_id) & (ratings["user_id"] == user_id)]
    if len(rating)==0:
        return 0
    return rating['rating'].tolist()[0]

def add_Rating(rating):
    ratings = getList('./data/rawdata/ratings.json')

    print(rating['rating'])
    check_rating = ratings[(ratings["item_id"] == rating["item_id"]) & (ratings["user_id"] == rating["user_id"])]
    if len(check_rating) == 0:
        try:
            new_ratings = pd.concat([ratings, pd.DataFrame([rating])], ignore_index=True)
            new_ratings.to_json("./data/rawdata/ratings.json", orient='records', lines=True)
        except FileNotFoundError:
            return False
    else:
        try:
            ratings.loc[((ratings["item_id"] == rating["item_id"]) & (ratings["user_id"] == rating["user_id"])), 'rating'] = rating["rating"]

            # ratings.to_csv("./data/ratings.csv", index=False)
            ratings.to_json("./data/rawdata/ratings.json", orient='records', lines=True)
        except FileNotFoundError:
            return False

    return True

def test():
    print('test')
# book

def list_KNNRecommendation(user_id, books):
    ratings =getList('./data/rawdata/ratings.json')
    list_bookid = service.getKNNRecommendation(user_id)
    list_books = []
    for i in list_bookid:
        book = books[books["item_id"] == i]
        book_json = book.to_dict(orient='records')
        list_books.append(book_json[0])

    for book in list_books:
         book['ratingavg'] = getRatingavg(book['item_id'], ratings)
    return list_books

def list_ALSRecommendation(user_id, books):
    ratings =getList('./data/rawdata/ratings.json')
    list_bookid = service.getALSRecommendation(user_id)
    list_books = []
    for i in list_bookid:
        book = books[books["item_id"] == i]
        book_json = book.to_dict(orient='records')
        list_books.append(book_json[0])

    for book in list_books:
         book['ratingavg'] = getRatingavg(book['item_id'], ratings)

    # print(list_books)
    return list_books

def list_CBRecommendation(book_name, ratings):
    top_k = CB.recommended_k_films_by_movie_name(book_name)
    for book in top_k:
        book['ratingavg'] = getRatingavg(book['item_id'], ratings)
    # print(top_k)
    return top_k

def list_DFRecommendation(ratings):
    top_k = DF.recommended(10)
    
    for book in top_k:
        book['ratingavg'] = getRatingavg(book["item_id"], ratings)
    return top_k

def list_hybridRecommendation(user_id, ratings):
    top_k = hybrid.hybrid_recommendation(user_id)
    for book in top_k:
        book['ratingavg'] = getRatingavg(book['item_id'], ratings)
    # print(top_k)
    return top_k

def getBookbyId(book_id, books, ratings):
    book = books[books["item_id"] == book_id]
    book = book.to_dict(orient='records')
    if len(book)==0:
        abort(404)
    book[0]['ratingavg'] = getRatingavg(book_id, ratings)
    return book[0]

def getListRandomBook(books, ratings):
    # ratings =getList('./data/rawdata/ratings.json')

    listBooks = books.sample(10)
    listBooks_json = listBooks.to_dict(orient='records')
    for book in listBooks_json:
         book['ratingavg'] = getRatingavg(book['item_id'], ratings)
    return listBooks_json

# user

# Hàm này trả về giá trị lớn nhất của user_id trong dữ liệu
def get_max_user_id(users):
    if len(users) ==0:
        return 0
    return users["user_id"].max()

# theem user
def add_new_user(user, users):
    new_users = pd.concat([users, pd.DataFrame([user])], ignore_index=True)
    try:
        new_users.to_json("./data/rawdata/users.json", orient='records', lines=True)
    except FileNotFoundError:
        return False

    return True
