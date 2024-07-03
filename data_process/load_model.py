from collections import defaultdict
import pickle
from surprise.dump import load

# Assuming the rest of your imports and functions are correctly defined

def get_top_n(predictions, n=20):
    """
    Generate the top-N recommendations for each user from a list of predictions.

    Args:
        predictions (list of Prediction objects): The list of predictions generated by the algorithm's test method.
        n (int): The number of recommendations to provide for each user. The default is 20.

    Returns:
        dict: A dictionary where the keys are user IDs and the values are lists of tuples:
              [(item ID, estimated rating), ...] containing the top N recommendations.
    """
    
    # Map the predictions to each user
    top_n = defaultdict(list)
    for user_id, item_id, true_rating, est_rating, _ in predictions:
        top_n[user_id].append((item_id, est_rating))
        
    # Sort the predictions for each user and retrieve the k highest ones
    for user_id, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[user_id] = user_ratings[:n]
        
    return top_n

# Load user watched list and threshold movie list
with open("models/user_watched.txt", "rb") as fp:
    user_watched_list = pickle.load(fp)
    
with open("models/threshold_movie_list.txt", "rb") as fp:
    threshold_movie_list = pickle.load(fp)   
    
# Load the algorithm and make predictions
algo = load("models/mini_model.pkl")[1]

# Assuming `user_set` is a list of tuples like [(username, ...), ...]
username = "monicanguyenh"
unwatched_movies = [x for x in threshold_movie_list if x not in user_watched_list]
prediction_set = [(username, x, 0) for x in unwatched_movies]

predictions = algo.test(prediction_set)
top_n = get_top_n(predictions, n=20)  

for uid, user_ratings in top_n.items(): 
    if uid == "monicanguyenh": 
        print(uid, [(iid, _) for (iid, _) in user_ratings])
