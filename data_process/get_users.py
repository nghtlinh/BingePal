import requests 
from bs4 import BeautifulSoup
import pymongo
from db_config import config
import certifi

# Extract user information and store data in a MongoDB database

db_name = "letterboxd"

client = pymongo.MongoClient(f'mongodb+srv://{config["MONGO_USERNAME"]}:{config["MONGO_PASSWORD"]}@cluster0.{config["MONGO_CLUSTER_ID"]}.mongodb.net/{db_name}?retryWrites=true&w=majority',
                             tlsCAFile=certifi.where())

db = client[db_name]
users = db.users

base_url = "https://letterboxd.com/members/popular/page/{}"
datafile = open('data_process/data/users.txt', 'w')

for page in range(1, 261):
    print("Page {}".format(page))
    
    r = requests.get(base_url.format(page))
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", attrs={"class": "person-table"})
    rows = table.findAll("td", attrs={"class": "table-person"})
    
    for row in rows:
        link = row.find("a")["href"]
        username = link.strip('/')
        display_name = row.find("a", attrs={"class":"name"}).text.strip()
        num_reviews = int(row.find("small").find("a").text.replace('xa0', ' ').split()[0].replace(',',''))
        
        user = {
            "username": username,
            "display_name": display_name,
            "num_reviews": num_reviews
        }
        
        #This is for local txt file in data/users.txt
        datafile.write(username + '\n')
        #this is for mongodb
        users.update_one({"username": user["username"]}, {"$set":user}, upsert=True)
        
datafile.close()
