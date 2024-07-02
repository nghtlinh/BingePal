import pandas as pd
from surprise import Dataset
from surprise import Reader
# from surprise import KNNWithMeans
from surprise import SVD
from surprise.model_selection import GridSearchCV
from surprise.model_selection import cross_validate
from surprise.dump import dump
import pickle

from get_user_ratings import get_user_data

# Load existing ratings data
df = pd.read_csv('data_process/data/sample_rating.csv')

# Get additional user ratings, Filter out movies that have been rated, and Added it into database
username = "monicanguyenh"
user_movies = get_user_data(username)
user_rated = [x for x in user_movies if x['rating_val'] > 0]

# Prepare data for training a recommendation model
user_df = pd.DataFrame(user_rated)
df = pd.concat([df, user_df]).reset_index(drop=True)


reader = Reader(rating_scale=(1,10))
data = Dataset.load_from_df(df[["user_id", "movie_id", "rating_val"]], reader)

# Train svd model
svd_algo = SVD()
train_set = data.build_full_trainset()
svd_algo.fit(train_set)

# Save model and data
dump("data_process/models/mini_model.pkl", predictions=None, algo=svd_algo, verbose=1)
pickle.dump(data, open("data_process/models/mini_model_data.pkl", "wb"))
