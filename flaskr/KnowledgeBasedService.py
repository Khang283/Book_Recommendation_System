import pandas as pd
import numpy as np
from pathlib import Path

class KnowledgeBasedService :
    def __init__(self,path):
        self.books = pd.read_csv(path+"/books.csv", encoding="utf-8",usecols=range(1,10))
        self.tags = pd.read_json(path+'/tags.json',lines=True)
        self.tag_count = pd.read_json(path+'/tag_count.json',lines=True)
        self.ratings = pd.read_json(path+'/ratings.json',lines=True)

        ### Prepare data
        self.df = pd.merge(self.books, self.tag_count, on='item_id',how='inner')
        self.df = pd.merge(self.df,self.tags,left_on='tag_id',right_on='id',how="inner").drop(columns=['id'])
        self.df = self.df.groupby('item_id', dropna=True).agg(tags=('tag','unique')).reset_index()
        self.df = pd.merge(self.books,self.df,on='item_id',how='inner')
    
    #Calculate average score of given books
    def calculate_score(self,bookId):
        return self.ratings[self.ratings['item_id']==bookId]['rating'].mean()
    
    #Get all the tag from all the books that user has read  
    def get_user_tags(self, userId):
        user = self.ratings[self.ratings['user_id']==userId]
        user_books = pd.merge(user,self.df,on='item_id',how='inner')
        tag_explode = user_books.explode('tags')
        tag_explode = tag_explode.groupby('tags').agg(appear=('tags','count'))
        tag_explode = tag_explode.sort_values(['appear'],ascending = False)
        tag_explode = tag_explode
        return tag_explode
    
    #Get recommendation for user, default is top 10
    def getRecommendBooks(self, userId, top=10):
        tags = self.get_user_tags(userId)[:top]
        tag_explode = self.df.explode('tags')
        result = pd.merge(tag_explode,tags,left_on='tags',right_on=tags.index,how='inner')
        result = result.groupby('item_id').agg(tags=('tags','unique')).reset_index()
        read_books = self.ratings[self.ratings['user_id']==userId]['item_id']
        result = result[~result['item_id'].isin(read_books)]
        #result['average_rating'] = result['item_id'].apply(lambda x: self.calculate_score(x))
        result = pd.merge(self.books,result,on='item_id',how='inner')
        result = result.sort_values('average_rating',ascending=False)
        return result[:top]
    

