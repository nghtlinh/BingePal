import pandas as pd

from numpy import asarray
from numpy import savetxt

import pymongo
from db_config import config 
import pickle

# Connect to Mongo DB Client
db_name = "letterboxd"
client = pymongo.MongoClient(f'mongodb+srv://{config["MONGO_USERNAME"]}:{config["MONGO_PASSWORD"]}@cluster0.{config["MONGO_CLUSTER_ID"]}.mongodb.net/{db_name}?retryWrites=true&w=majority')

# Access + query collections 
db = client[db_name]
ratings = db.ratings
users = db.users

# Fetch specific user ratings
my_ratings = ratings.find(
    {"user_id": "monicanguyenh"}, 
    {"user_id": 1, "movie_id": 1, "rating_val": 1, "_id": 0}
)
print(my_ratings)
# Fetch random sample ratings
all_ratings = ratings.aggregate([
    {"$sample": {"size": 250000}}
])

# Combine and convert to DataFrame
all_ratings = list(all_ratings) + list(my_ratings)
# Create a Pandas DataFrame from the combined list of documents
df = pd.DataFrame(all_ratings)
df = df[["user_id", "movie_id", "rating_val"]]

df.to_csv('data_process/data/sample_rating_data.csv', index=False)

min_review_threshold = 8

# Group the DataFrame by movie_id and caculate the sum of rating_val for each group
# Result dataframe where each row represents a 'movie_id' + sum of 'rating_val' for that movie
grouped_df = df.groupby(by=["movie_id"]).sum()

# Filters rows of grouped_df where sum of rating_val > the min_review_threshold.
grouped_df = grouped_df.loc[grouped_df['rating_val'] > min_review_threshold]

grouped_df.reset_index(inplace=True)
# grouped_df.to_csv("models/threshold_movie_list.csv")

with open('data_process/models/threshold_movie_list.txt', 'wb') as fp:
    pickle.dump(grouped_df["movie_id"].to_list(), fp)
