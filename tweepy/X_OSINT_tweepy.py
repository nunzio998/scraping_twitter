import tweepy
import pandas as pd
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

# Instantiate the tweepy API
api = tweepy.API(auth, wait_on_rate_limit=True)

search_query = "'ref''hacker'-filter:retweets AND -filter:replies AND -filter:links"
num_tweets = 100

try:
    # The number of tweets we want to retrieved from the search
    tweets = api.search_tweets(q=search_query, lang="en", count=num_tweets, tweet_mode='extended')

    # Pulling Some attributes from the tweet
    attributes_container = [[tweet.user.name, tweet.created_at, tweet.favorite_count, tweet.source, tweet.full_text] for
                            tweet in tweets]

    # Creation of column list to rename the columns in the dataframe
    columns = ["User", "Date Created", "Number of Likes", "Source of Tweet", "Tweet"]

    # Creation of Dataframe
    tweets_df = pd.DataFrame(attributes_container, columns=columns)
except BaseException as e:
    print('Status Failed On,', str(e))
