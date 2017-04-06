# -*- coding: utf-8 -*-
import pprint
import time
from datetime import datetime, timedelta
from email.utils import parsedate_tz

import pymongo
import tweepy
from pymongo import MongoClient

pp = pprint.PrettyPrinter(indent=4)

TWEEPY_CONSUMER_KEY = 'OjRhUCjzV5DV4FqvHLJCw805g'
TWEEPY_CONSUMER_SECRET = 'xK2yq4mIFYN6Oz9tBCNdF6YrK1O1k1kyzaPzCgqyWUC74rppZL'
TWEEPY_ACCESS_TOKEN_KEY = '431741922-1Tstc2CDFgzA8FoSgp20C8fQR4MXwx18dkPtNXXM'
TWEEPY_ACCESS_TOKEN_SECRET = '494ybkd0FK4IQQ3dSiBYEONbFHeIVsH3geN71kXTX0QHD'

auth = tweepy.OAuthHandler(TWEEPY_CONSUMER_KEY, TWEEPY_CONSUMER_SECRET)
auth.set_access_token(TWEEPY_ACCESS_TOKEN_KEY, TWEEPY_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)
client = MongoClient('localhost', 27017)

db = client.cz4034
tweets_collection = db.tweets

tweets_collection.ensure_index([('id', pymongo.ASCENDING)])

searchQuery = 'realDonaldTrump -filter:retweets'  # this is what we're searching for
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


def to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


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
                json_tweet['created_at'] = to_datetime(json_tweet['created_at'])
                json_tweet['search_query'] = 'realDonaldTrump'
                bulk.find({'id': tweet.id}).upsert().update({'$setOnInsert': json_tweet})
        bulk.execute()
        tweetCount += len(new_tweets)
        print("Downloaded {0} tweets".format(tweetCount))
        max_id = new_tweets[-1].id
    except tweepy.TweepError as e:
        # Just exit if any error
        print("some error : " + str(e))
        time.sleep(60)

print("Downloaded {0} tweets".format(tweetCount))
