import json
import random
import pandas as pd
from werkzeug.exceptions import abort

def getList(url):
    # data=[]
    # with open(url, 'r') as f:
    #     for line in f:
    #             data.append(json.loads(line))
    print(url)
    data = pd.read_csv(url)
    # data = data.to_dict(orient='records')
    return data

def getRatingavg(book_id, ratings):
    # list_ratings = []
    # for rating in ratings:
    #     if (book_id ==rating['item_id']):
    #         list_ratings.append(rating)
    # if (len(list_ratings) ==0):
    #      return 0
    # total_rating = sum(rating["rating"] for rating in list_ratings)
    # average_rating = total_rating / len(list_ratings)

    rating_movie = ratings[ratings["item_id"] == book_id]
    average_rating = rating_movie["rating"].mean()

    return round(average_rating, 2)

def getRatingBookByUser(book_id, user_id, ratings):
    rating = ratings[(ratings["item_id"] == book_id) & (ratings["user_id"] == user_id)]
    if len(rating)==0:
        return 0
    return rating['rating'].tolist()[0]

def add_Rating(rating):
    ratings = getList('./data/ratings.csv')

    print(rating['rating'])
    check_rating = ratings[(ratings["item_id"] == rating["item_id"]) & (ratings["user_id"] == rating["user_id"])]
    if len(check_rating) == 0:
        try:
            new_ratings = pd.concat([ratings, pd.DataFrame([rating])], ignore_index=True)
            new_ratings.to_csv("./data/ratings.csv", index=False)
        except FileNotFoundError:
            return False
    else:
        try:
            ratings.loc[((ratings["item_id"] == rating["item_id"]) & (ratings["user_id"] == rating["user_id"])), 'rating'] = rating["rating"]

            ratings.to_csv("./data/ratings.csv", index=False)
        except FileNotFoundError:
            return False

    return True

def test():
    print('test')
# book

def getBookbyId(book_id, books, ratings):
    book = books[books["item_id"] == book_id]
    book = book.to_dict(orient='records')
    if len(book)==0:
        abort(404)
    book[0]['ratingavg'] = getRatingavg(book_id, ratings)
    return book[0]

def getListRandomBook(books):
    ratings =getList('./data/ratings.csv')

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
        new_users.to_csv("./data/users.csv", index=False)
    except FileNotFoundError:
        return False

    return True
