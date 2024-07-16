from create_training_data import create_training_data
from build_model import build_model
from run_model import run_model
import pickle
import pymongo
import pymongo.errors
from surprise.dump import load, dump
from surprise.dump import dump


def main():
    print("Welcome to the username prompt CLI!")
    username = input("Please enter your username: ")

    print("================================")
    print("Creating Training Data Sample...")
    print("================================")
    success = False
    while success == False:
        try:
            training_df, threshold_movie_list = create_training_data(200000)
            success = True
        except pymongo.errors.OperationFailure:
            print("Encountered $sample operation error. Retrying...")
    
    with open('models/threshold_movie_list.txt', 'wb') as fp:
        pickle.dump(threshold_movie_list, fp)
        
    training_df.to_csv('data/training_data.csv', index=False)


    print("=================")
    print("Building Model...")
    print("=================")
    build_model(username)

    svd_algo, user_watched_list = build_model(username)    
    
    dump("models/mini_model.pkl", predictions=None, algo=svd_algo, verbose=1)
    with open("models/user_watched.txt", "wb") as fp:
        pickle.dump(user_watched_list, fp)
    

    print("================")
    print("Running Model...")
    print("================")
    with open("models/user_watched.txt", "rb") as fp:
        user_watched_list = pickle.load(fp)

    with open("models/threshold_movie_list.txt", "rb") as fp:
        threshold_movie_list = pickle.load(fp)

    algo = load("models/mini_model.pkl")[1]

    run_model(username, algo, user_watched_list, threshold_movie_list, 25)

    print("=========")
    print("Finished!")
    print("=========")

if __name__ == "__main__":
    main()