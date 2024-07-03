from collections import defaultdict
import pickle
from surprise.dump import load


def get_top_n(predictions, n=20):
    top_n = [(item_id, est_rating) for user_id, item_id, true_rating, est_rating, _ in predictions]
    top_n.sort(key=lambda x: x[1], reverse=True)
        
    return top_n[:n]

# Load user watched list and threshold movie list
with open("models/user_watched.txt", "rb") as fp:
    user_watched_list = pickle.load(fp)
    
with open("models/threshold_movie_list.txt", "rb") as fp:
    threshold_movie_list = pickle.load(fp)   
    
# Load the algorithm and make predictions
algo = load("models/mini_model.pkl")[1]

# Assuming `user_set` is a list of tuples like [(username, ...), ...]
username = "panukadu"
unwatched_movies = [x for x in threshold_movie_list if x not in user_watched_list]
prediction_set = [(username, x, 0) for x in unwatched_movies]

# Generate prediction for a single user panukadu
predictions = algo.test(prediction_set)
top_n = get_top_n(predictions, n=20)  
        
# Print recommended movies for user
for prediction in top_n:
    print(f"{prediction[0]}: {round(prediction[1], 2)}")
