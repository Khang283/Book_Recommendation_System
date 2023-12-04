import pandas as pd
import numpy as np
from pathlib import Path

class CFService:
    def __init__(self) -> None:
        pathKNN = Path('../data/knn_prediction.csv')
        pathALS = Path('../data/als_prediction.csv')
        self.knn = pd.read_csv(pathKNN,header=0,names=['user_id','item_id','rating','prediction','detail'])
        self.als = pd.read_csv(pathALS,names=['item_id','user_id','rating','prediction'])
        pass

    #Param: id -> user_id in the dataframe
    #Return: [] -> list of item_id if the user is not in the list return empty []
    def getKNNRecommendation(self,id):
        if id not in self.knn['user_id']:
            return []
        return self.knn[self.knn['user_id']==id]['item_id'].to_list()
    
    def getALSRecommendation(self,id):
        if id not in self.als['user_id']:
            return []
        return self.als[self.als['user_id']==id]['item_id'].to_list()
