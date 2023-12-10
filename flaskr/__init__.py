import os

from flask import Flask
from flaskr import contentbased as CB
from flaskr import demographicfiltering as DF


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/")
    def hello():
        return "Hello, World!"

    @app.route("/test")
    def contentbased_for_user():
        userId = 28
        contentbased_rs_list = CB.w2v_recommendation(userId, 10)
        if contentbased_rs_list is not None:
            return contentbased_rs_list
        return []

    @app.route("/test2")
    def contentbased_on_book():
        movie_name = "The Hunger Games (The Hunger Games, #1)"
        top_k = CB.recommended_k_films_by_movie_name(movie_name)
        return top_k

    @app.route("/test3")
    def demographicfiltering():
        top_k = DF.recommended(10)
        return top_k

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
