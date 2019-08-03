import tweepy
import config
from pymongo import MongoClient
import json

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

MONGO_HOST= 'mongodb://localhost/tweets'
api = tweepy.API(auth)
#ITASWE
#ItalySweden
#Russia2018
#WCQ

results = api.search(q="ITASWE", since_id=930099181313777664, max_id=930268672681062406)

for result in results:
    #client = MongoClient(MONGO_HOST)
    #db = client.tweets
    #print result
    #datajson = json.loads(result)
    created_at = result.created_at

    print("Tweet collected at " + result.text)
    #db.match_tweets.insert(datajson)