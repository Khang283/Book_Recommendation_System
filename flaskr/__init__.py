import os

from flask import Flask
from flaskr import contentbased
from flaskr import content_based


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
    def contentbasedRS():
        userId = 100
        contentbased_rs_list = contentbased.contentbasedRecommendationSystem(userId)
        if contentbased_rs_list is not None:
            return contentbased_rs_list
        return "khong tim thay"

    @app.route("/test2")
    def contentbasedRS2():
        movie_name = "The Hunger Games (The Hunger Games, #1)"
        top_k = contentbased.recommended_k_films_by_movie_name(movie_name)
        return top_k

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
