import os
import random

from flaskr import module
from werkzeug.exceptions import abort

from flask import Flask, render_template, request


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
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
    
    @app.route('/home')
    @app.route('/')
    def home():
        books =module.getListRandomBook()
        return render_template('home.html', books =books)
    
    @app.route('/<int:book_id>', methods=['GET', 'POST'])
    def detail(book_id):
        book = module.getBookbyId(book_id)

        # if request.method == 'POST':
        #     rating = request.form.get('rating')
        #     print(rating)
            # comment = request.form.get('comment')

        return render_template('detail.html', book=book)

    return app