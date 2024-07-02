import pandas as pd
from surprise import Dataset
from surprise import Reader
# from surprise import KNNWithMeans
from surprise import SVD
from surprise.model_selection import GridSearchCV
from surprise.model_selection import cross_validate
from surprise.dump import dump
import pickle

#load ratings data
df = pd.read_csv('data_process/data/sample_rating.csv')

reader = Reader(rating_scale=(1,10))
data = Dataset.load_from_df(df[["user_id", "movie_id", "rating_val"]], reader)

svd_algo = SVD()
# cross_validate(svd_algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

train_set = data.build_full_trainset()
svd_algo.fit(train_set)
dump("data_process/models/mini_model.pkl", predictions=None, algo=svd_algo, verbose=1)
pickle.dump(data, open("data_process/models/mini_model_data.pkl", "wb"))
