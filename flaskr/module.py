import json
import random
from werkzeug.exceptions import abort

def getList(url):
    data=[]
    with open(url, 'r') as f:
        for line in f:
                data.append(json.loads(line))
    print(url)
    return data

books = getList('./data/metadata.json')
ratings =getList('./data/ratings.json')

def getRatingavg(book_id, ratings):
    list_ratings = []
    for rating in ratings:
        if (book_id ==rating['item_id']):
            list_ratings.append(rating)
    if (len(list_ratings) ==0):
         return 0
    total_rating = sum(rating["rating"] for rating in list_ratings)
    average_rating = total_rating / len(list_ratings)
    return round(average_rating, 2)

def getRatingBookByUser(book_id, user_id):
    rating =[i for i in ratings if book_id == i['item_id'] and user_id == i['user_id']]
    if len(rating)==0:
        return 0
    return rating[0]['rating']

def add_Rating(rating):

    ratings.append(rating)
    print(rating['rating'])
    if rating not in ratings:
        try:
            with open("./data/rating.json", 'w') as file:
                for obj in ratings:
                    json.dump(obj, file)
                    file.write('\n')
        except FileNotFoundError:
            return False
    else:
        for entry in ratings:
            if entry.get("item_id") == rating['item_id'] and entry.get("user_id") == rating['user_id']:
                entry = rating
                print(entry['rating'])
                break
        try:
            with open("./data/ratings.json", 'w') as file:
                for obj in ratings:
                    json.dump(obj, file)
                    file.write('\n')
        except FileNotFoundError:
            return False

    return True

def test():
    print('test')
# book

def getBookbyId(book_id):
    # books = getList('./data/metadata.json')
    # ratings =getList('./data/ratings.json')

    book = [i for i in books if book_id == i['item_id']]
    if len(book)==0:
        abort(404)
    book[0]['ratingavg'] = getRatingavg(book_id, ratings)
    return book[0]

def getListRandomBook():
    # books = getList('./data/metadata.json')
    # ratings =getList('./data/ratings.json')

    listBooks = random.sample(books,10)
    for book in listBooks:
         book['ratingavg'] = getRatingavg(book['item_id'], ratings)
    return listBooks

# user

# Hàm này trả về giá trị lớn nhất của user_id trong dữ liệu
def get_max_user_id(users):
    if not users:
        return 0
    return max(item['user_id'] for item in users)

# theem user
def add_new_user(user, users):
    users.append(user)
    try:
        with open("./data/users.json", 'w') as file:
            for obj in users:
                json.dump(obj, file)
                file.write('\n')
    except FileNotFoundError:
        return False

    return True
