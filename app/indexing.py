# -*- coding: utf-8 -*-
import pprint

import pymongo
import yaml
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm

pp = pprint.PrettyPrinter(indent=4)

es = Elasticsearch()

client = pymongo.MongoClient('localhost', 27017)
db = client.cz4034
parsed_tweets_collection = db.tweets_parsed

es.indices.delete(index='tweets', ignore=[400, 404])

tweets_cursor = parsed_tweets_collection.find()
total_count = tweets_cursor.count()

id_count = 0
bulk_count = 0
index_every = 10000
tweet_list = []

f = open('./tweet_mapping.yml')
# use safe_load instead load
tweet_mapping = yaml.safe_load(f)
f.close()

print(tweet_mapping)

es.create(index='tweets', doc_type='tweet', id=1, ignore=400, body=tweet_mapping)

for tweet in tqdm(tweets_cursor, total=total_count):
    try:
        bulk_count += 1
        del tweet['_id']
        tweet['_type'] = 'tweet'
        tweet['_index'] = 'tweets'
        tweet_list.append(tweet)
        # res = es.index(index="tweets", doc_type='tweet', id=id_count, body=dumps(tweet))
        if bulk_count >= index_every:
            helpers.bulk(es, tweet_list)
            tweet_list = []
            bulk_count = 0
    except Exception as e:
        pp.pprint(tweet)
        print(e)
if bulk_count > 0:
    helpers.bulk(es, tweet_list)

es.indices.refresh(index="tweets")
