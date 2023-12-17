import pandas as pd
import os
import numpy as np
from surprise import Reader, Dataset, SVD
from flaskr import contentbased as CB


def joinPath(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", file_name)
    return file_path


books = pd.read_json(joinPath("metadata.json"), lines=True)
ratings = pd.read_json(joinPath("ratings.json"), lines=True)

reader = Reader()


data = Dataset.load_from_df(ratings[["user_id", "item_id", "rating"]], reader)

svd = SVD()

trainset = data.build_full_trainset()

svd.fit(trainset)


def hybrid_recommendation(userId, k):
    top_k = CB.w2v_recommendation(userId, 3 * k)
    item_ids = top_k["item_id"].values
    ratings_predict = [svd.predict(userId, item_id).est for item_id in item_ids]
    top_k["est"] = ratings_predict
    top_k = top_k.sort_values("est", ascending=False).head(k)
    return top_k.drop(["cos_sim", "est"], axis=1).to_dict(orient="records")
