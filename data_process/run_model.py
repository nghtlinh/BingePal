from collections import defaultdict

from surprise import Dataset
from surprise import SVD
from surprise import Reader
from surprise.model_selection import GridSearchCV
from surprise import SVD
from surprise.dump import load
from load_model import get_top_n

import pickle

import pandas as pd

def run_model(username, algo, user_watched_list, threshold_movie_list, num_recommendations=20):
    
    unwatched_movies = [x for x in threshold_movie_list if x not in user_watched_list]
    prediction_set = [(username, x, 0) for x in unwatched_movies]
    
    predictions = algo.test(prediction_set)
    top_n = get_top_n(predictions, num_recommendations)
    
    for prediction in top_n:
        print(f"{prediction[0]}: {round(prediction[1], 2)}")
    
    return top_n

if __name__ == "__main__":
    with open("models/user_watched.txt", "rb") as fp:
        user_watched_list = pickle.load(fp)

    with open("models/threshold_movie_list.txt", "rb") as fp:
        threshold_movie_list = pickle.load(fp)

    algo = load("models/mini_model.pkl")[1]

    run_model("panukadu", algo, user_watched_list, threshold_movie_list, 25)