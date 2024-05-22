from ntscraper import Nitter
import json
from utils import *

#termini = ["killnet", "hacker"]

results = Nitter(log_level=1, skip_instance_check=False).get_tweets("github", mode='hashtag')

client = connect_to_mongo()

collection = connect_to_mongo_collection(client, "prova")

with open("tweets.json", "w") as f:
    json.dump(results, f)

#dict_to_save = tweets['tweets'][0]

#save_to_mongo(dict_to_save, collection)
print("fine")