import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise.model_selection import GridSearchCV
from surprise.model_selection import cross_validate
from surprise.dump import dump
import pickle

from get_user_ratings import get_user_data

def build_model(username):
        
    df = pd.read_csv('data/training_data.csv')
    
    user_movies = get_user_data(username)
    user_rated = [x for x in user_movies if x['rating_val'] > 0]
    
    # Prepare data for training a recommendation model
    user_df = pd.DataFrame(user_rated)
    df = pd.concat([df, user_df]).reset_index(drop=True)
    df.drop_duplicates(inplace=True)

    # Load surprise dataset
    reader = Reader(rating_scale=(1,10))
    data = Dataset.load_from_df(df[["user_id", "movie_id", "rating_val"]], reader)

    # Train svd model
    svd_algo = SVD()
    train_set = data.build_full_trainset()
    svd_algo.fit(train_set)
    user_watched_list = [x['movie_id'] for x in user_movies]
    
    return svd_algo, user_watched_list


if __name__ == "__main__":
    with open("config/user_config.txt", "r") as f:
        username = f.read().strip()

    svd_algo, user_watched_list = build_model(username)    
    
    dump("models/mini_model.pkl", predictions=None, algo=svd_algo, verbose=1)
    with open("models/user_watched.txt", "wb") as fp:
        pickle.dump(user_watched_list, fp)