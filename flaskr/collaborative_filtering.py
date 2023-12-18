import findspark 
findspark.init()
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
import pandas as pd
import numpy as np
from pathlib import Path
import json
from sklearn.metrics.pairwise import linear_kernel

spark = SparkSession.builder.appName('Collaborative Filtering').getOrCreate()

ratings = spark.read.json('../data/ratings.json')

ratings.printSchema()

ratings.show(5)

train, test = ratings.randomSplit([.8, .2])

als = ALS(maxIter=10,
          regParam= 0.1,
          rank=5,
          userCol='user_id',
          ratingCol='rating',
          itemCol='item_id')
model = als.fit(train)
prediction = model.transform(test)
prediction = prediction.where(f.col('prediction')!=np.nan)
evaluator = RegressionEvaluator(metricName='rmse',
                                labelCol='rating',
                                predictionCol='prediction')
rmse = evaluator.evaluate(prediction)

print(rmse)
prediction.show(5)






