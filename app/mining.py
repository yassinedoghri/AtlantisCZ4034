# -*- coding: utf-8 -*-
import pprint
import time

import pymongo
import tweepy
from pymongo import MongoClient

pp = pprint.PrettyPrinter(indent=4)

TWEEPY_CONSUMER_KEY = 'your_consumer_key'
TWEEPY_CONSUMER_SECRET = 'your_consumer_secret'
TWEEPY_ACCESS_TOKEN_KEY = 'your_access_token'
TWEEPY_ACCESS_TOKEN_SECRET = 'your_access_token_secret'

auth = tweepy.OAuthHandler(TWEEPY_CONSUMER_KEY, TWEEPY_CONSUMER_SECRET)
auth.set_access_token(TWEEPY_ACCESS_TOKEN_KEY, TWEEPY_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)
client = MongoClient('localhost', 27017)

db = client.cz4034
tweets_collection = db.tweets

tweets_collection.ensure_index([('id', pymongo.ASCENDING)])

searchQueryList = ['trump immigration -filter:retweets',
                   'trump obamacare -filter:retweets',
                   'trump syria -filter:retweets',
                   'trump russia -filter:retweets',
                   'trump wall -filter:retweets',
                   'realDonaldTrump -filter:retweets']  # this is what we're searching for

for searchQuery in searchQueryList:
    maxTweets = 10000000  # Some arbitrary large number
    tweetsPerQry = 100  # this is the max the API permits
    language = 'en'

    # If results from a specific ID onwards are reqd, set since_id to that ID.
    # else default to no lower limit, go as far back as API allows
    sinceId = None

    # If results only below a specific ID are, set max_id to that ID.
    # else default to no upper limit, start from the most recent tweet matching the search query.
    max_id = -1
    tweetCount = 0

    print("Downloading max {0} tweets".format(maxTweets))
    while tweetCount < maxTweets:
        try:
            if max_id <= 0:
                if not sinceId:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang=language)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang=language, since_id=sinceId)
            else:
                if not sinceId:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang=language, max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang=language, max_id=str(max_id - 1),
                                            since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            bulk = tweets_collection.initialize_ordered_bulk_op()
            for tweet in new_tweets:
                if (not tweet.retweeted) and ('RT @' not in tweet.text):
                    json_tweet = tweet._json
                    bulk.find({'id': tweet.id}).upsert().update({'$setOnInsert': json_tweet})
            bulk.execute()
            tweetCount += len(new_tweets)
            print("Downloaded {0} tweets for {1}".format(tweetCount, searchQuery))
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # wait if any error
            print("some error : " + str(e))
            time.sleep(60)
    print("Downloaded {0} tweets".format(tweetCount))
