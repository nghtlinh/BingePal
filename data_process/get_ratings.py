import asyncio
from aiohttp import ClientSession
import requests
from pprint import pprint

from bs4 import BeautifulSoup

import pymongo
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

import motor.motor_asyncio
from config import config

import time

# Fetch page's content
async def fetch(url, session, input_data={}):
    async with session.get(url) as response:
        if input_data != {}:
            return await response.read(), input_data
        else: 
            return await response.read()
   
# Fetch page counts + Update MongoDB documents     
async def get_page_counts(usernames, db_cursor):
    url = "https://letterboxd.com/{}/films/ratings/"
    tasks = []
    
    async with ClientSession() as session:
        for username in usernames:
            task = asyncio.ensure_future(fetch(url.format(username), 
                                               session, {"username": username}))
            tasks.append(task)
        
        # Gather the results
        responses = await asyncio.gather(*tasks)
        
        # Process each response
        for response in responses:
            soup = BeautifulSoup(response[0], "html.parser")
            try:
                page_link = soup.findAll("li", attrs={"class", "paginate_page"})[-1]
                num_pages = int(page_link.find("a").text.replace(',', ''))
            except IndexError:
                num_pages = 1
                
            
            users.update_one({"username": response[1]['username']},
                             {"$set": {"num_ratings_pages": num_pages}})
            
    
async def generate_rating_upsert_operations(response):
    
    # Parse ratings page response for each rating/review using lxml for faster processing
    soup = BeautifulSoup(response[0], "lxml")
    reviews = soup.findAll("li", attrs={"class": "poster-container"})
    
    # Create empty array to store list of bulk UpdateOne operations (MongoDB update operations)
    operations = []
    
    # For each review, parse data from scraped HTML page + Append an UpdateOne operation for bulk execution
    for review in reviews:
        movie_id = review.find('div', attrs={"class", "film-poster"})['data-target-link'].split('/')[-2]
        
        rating_class = review.find("span", attrs={"class":"rating"})['class'][1]
        rating_val = int(rating_class.split('-')[-1])
        
        # MongoDB update operation
        operations.append(UpdateOne({
            "user_id": response[1]["username"],
            "movie_id": movie_id
        },
        {
            "$set": {
                "movie_id": movie_id,
                "rating_val": rating_val,
                "user_id": response[1]["username"]
            }
        }, 
        upsert = True
        ))
        
        return operations
    
    
    # Fetch and process user ratings then update MongoDB database with fetched data
    async def get_ratings(usernames, db_cursor, mongo_db):
        start = time.time()
        print("Function Start")
        
        url = "https://letterboxd.com/{}/films/ratings/page/{}/"
        
        # Create/reference "ratings" collection in db
        ratings = db.ratings
        
        # Loop through each user
        for i, username in enumerate(usernames):
            print(i, username)
            
            # Look up user in MongoDB database and retrieve the number of rating pages
            user = db_cursor.find_one({"username": username})
            num_pages = user["num_rating_pages"]
            
            # Fetch all responses within aiohttp ClientSession and keep connection alive for all requests
            async with ClientSession() as session:
                print("Starting Scrape", time.time() - start)
                
                # Task queue for all async fetch tasks
                tasks = []
                
                # Make a request for each ratings page and add to task queue
                for i in range(num_pages):
                    # Format the URL with username and page number
                    task = asyncio.ensure_future(fetch(url.format(username, i), session, user))
                    tasks.append(task)
                    
                parse_responses = await asyncio.gather(*tasks)
                
                # Concatenate each response's upsert operations
                upsert_operations = []
                for response in parse_responses:
                    upsert_operations += response
                
                print("Starting Upsert", time.time() - start)
                
                # Execute bulk upsert operations
                try: 
                    if len(upsert_operations) > 0:
                        ratings.bulk_write(upsert_operations, ordered=False)
                except BulkWriteError as bwe:
                    print(bwe.details)
                    
                print("Finishing Upsert", time.time() - start)   
                

# Connect to MongoDB Client                
db_name = config["MONGO_DB"]

client = pymongo.MongoClient(f'mongodb+srv://{config["MONGO_USERNAME"]}:
                             {config["MONGO_PASSWORD"]}
                             @cluster0.{config["MONGO_CLUSTER_ID"]}.
                             mongodb.net/{db_name}?retryWrites=true&w=majority')

# Find Letterbox databse and user collection
db = client[db_name]
users = db.users
all_users = users.find({})
all_usernames = [x['username'] for x in all_users] + ["samlearner"]

loop = asyncio.get_event_loop()

# Find number of ratings pages for each user and add to their Mongo document
future = asyncio.ensure_future(get_page_counts([], users))
loop.run_until_complete(future)

# Find and store ratings for each user
future = asyncio.ensure_future(get_ratings(all_usernames[1800:], users, db))

loop.run_until_complete(future)