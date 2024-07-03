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

# # Fetch specific user ratings
# my_ratings = ratings.find(
#     {"user_id": "monicanguyenh"}, 
#     {"user_id": 1, "movie_id": 1, "rating_val": 1, "_id": 0}
# )
# print(my_ratings)
# # Fetch random sample ratings
# all_ratings = ratings.aggregate([
#     {"$sample": {"size": 250000}}
# ])

# Sample dataset ratings into chunks to have a sample set
all_ratings = []
target_sample_size = 200000
sample_size = int(target_sample_size*1.15)
max_chunk_size = 30000
num_iterations = 1 + (sample_size // max_chunk_size)

for i in range(num_iterations):
    iteration_size = min(max_chunk_size, sample_size - (max_chunk_size * i)) 
    
    rating_sample = ratings.aggregate([
        {"$sample": {"size": iteration_size}}
    ])
    
    all_ratings += list(rating_sample)

# Create a Pandas DataFrame from the combined list of all ratings
df = pd.DataFrame(all_ratings)
df = df[["user_id", "movie_id", "rating_val"]]
print("DataFrame's size:  ")
print("Before removing duplicates: ", df.shape)
df.drop_duplicates(inplace=True)
print("After removing duplicates: ", df.shape)

df.to_csv('data/sample_rating_data.csv', index=False)

min_review_threshold = 5

# Group the DataFrame by movie_id and caculate the sum of rating_val for each group
grouped_df = df.groupby(by=["movie_id"]).sum()

# Filters rows of grouped_df where sum of rating_val > the min_review_threshold.
grouped_df = grouped_df.loc[grouped_df['rating_val'] > min_review_threshold]

grouped_df.reset_index(inplace=True)

with open('models/threshold_movie_list.txt', 'wb') as fp:
    pickle.dump(grouped_df["movie_id"].to_list(), fp)
