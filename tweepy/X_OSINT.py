import tweepy
import json

def read_json(path):
    with open(path, 'r') as file:
        return json.load(file)

# Load the twitter API keys from the json file
keys = read_json('tweepy_keys.json')

# Pass in our twitter API authentication key
auth = tweepy.OAuth1UserHandler(
    keys['consumer_key'], keys['consumer_secret'], keys['access_token'], keys['access_token_secret']
)
api = tweepy.API(auth, wait_on_rate_limit=True)



# Esecuzione della ricerca dei tweet
x_users = api.get_user(screen_name='@killnet')

# Stampare i testi dei tweet trovati
for user in x_users:
    print(user.text)
