import json
import random
from werkzeug.exceptions import abort

def getListBooks():
    data=[]
    with open('./data/metadata.json', 'r') as f:
        for line in f:
                data.append(json.loads(line))
    return data

def getListRatings():
    data=[]
    with open('./data/ratings.json', 'r') as f:
        for line in f:
                data.append(json.loads(line))
    return data

books = getListBooks()
ratings =getListRatings()

def getRatingavg(book_id):
    list_ratings = []
    for rating in ratings:
        if (book_id ==rating['item_id']):
            list_ratings.append(rating)
    if (len(list_ratings) ==0):
         return 0
    total_rating = sum(rating["rating"] for rating in list_ratings)
    average_rating = total_rating / len(list_ratings)
    return round(average_rating, 2)

def getBookbyId(book_id):

    book = [i for i in books if book_id == i['item_id']]
    if book is None:
        abort(404)
    book[0]['ratingavg'] = getRatingavg(book_id)
    return book[0]

def getListRandomBook():
    listBooks = random.sample(books,10)
    for book in listBooks:
         book['ratingavg'] = getRatingavg(book['item_id'])
    return listBooks


