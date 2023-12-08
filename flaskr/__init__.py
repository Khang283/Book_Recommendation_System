import os
import random

from flaskr import module
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, request, redirect, url_for, session


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'your_secret_key'
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/test')
    def index():
        return render_template('index.html')
    
    # page home
    @app.route('/home')
    @app.route('/')
    def home():
        user = session.get('user')
        list_books = module.getList("./data/books.csv")
        books_random =module.getListRandomBook(list_books)
        return render_template('home.html', books =books_random, user=user)
    
    # page detail
    @app.route('/<int:book_id>', methods=['GET', 'POST'])
    def detail(book_id):
        list_books = module.getList('./data/books.csv')
        ratings =module.getList('./data/ratings.csv')
        # module.test()
        book = module.getBookbyId(book_id, list_books, ratings)

        books_random =module.getListRandomBook(list_books)

        if 'user' in session:
            user = session.get('user')
            rating_user = module.getRatingBookByUser(book_id, user['user_id'], ratings)
            return render_template('detail.html', book=book, user=user, rating_user= rating_user, books = books_random)
        
        # if request.method == 'POST':
        #     module.test()
        #     rating_input = request.form['rating-input']
        #     module.test()
        #     rating = {
        #         "item_id": book_id,
        #         "user_id": session.get('user')['user_id'],
        #         "rating": rating_input
        #     }
        #     module.test()

        #     module.add_Rating(rating)
        #     # print(rating)
        #     return redirect(url_for('detail', book_id))
            # return render_template('detail.html', book=book, user=user, rating_user= rating)

        return render_template('detail.html', book=book, books = books_random)
    
    @app.route('/submit_rating', methods=['POST'])
    def submit_rating():
        if request.method == 'POST':
            rating_input = request.form['rating-input']
            book_id = request.form['book_id']
            # ratings =module.getList('./data/ratings.csv')
            rating = {
                "item_id": int(book_id),
                "user_id": session.get('user')['user_id'],
                "rating": int(rating_input)
            }

            if module.add_Rating(rating):
                return redirect(url_for('detail', book_id = book_id))
            else:
                error = 'Đánh giá không thành công'
                return render_template('detail.html', error=error)
    
    # page register
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            users = module.getList('./data/users.csv')
            user_id = module.get_max_user_id(users) +1

            if username not in users["username"].tolist():
                user = {
                    "user_id": user_id,
                    "username": username,
                    "password": hashed_password
                }
                if module.add_new_user(user, users):
                    return redirect(url_for('login'))
                else:
                    error = 'Không thể đăng kí, xin vui lòng đăng kí lại.'
                    return render_template('register.html', error=error)
                
            else:
                # Tên người dùng đã tồn tại, hiển thị thông báo lỗi.
                error = 'Tên này đã có người dùng. Xin hãy chọn tên người dùng khác.'
                return render_template('register.html', error=error)

        return render_template('register.html')
    
    # page login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            users = module.getList('./data/users.csv')
            user = users[users["username"] == username]
            # user = [i for i in users if username == i['username']]
            if len(user) ==0:
                error = 'Đăng nhập không hợp lệ. Làm ơn kiểm tra tên người dùng của bạn.'
                return render_template('login.html', error=error)
            else:
                if check_password_hash(user['password'].tolist()[0], password):
                    user_sesion = {
                        "username": username,
                        "user_id": user['user_id'].tolist()[0]
                    }
                    session['user'] = user_sesion
                    return redirect(url_for('home'))
                else:
                    error = 'Đăng nhập không hợp lệ. Làm ơn kiểm tra mật khẩu của bạn.'
                    return render_template('login.html', error=error)

        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect(url_for('login'))

    return app