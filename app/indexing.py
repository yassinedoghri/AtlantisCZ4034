# -*- coding: utf-8 -*-
import pymongo
from elasticsearch import Elasticsearch, helpers
from bson.json_util import dumps
import yaml

es = Elasticsearch()

client = pymongo.MongoClient('localhost', 27017)
db = client.cz4034
tweets_collection = db.tweets

es.indices.delete(index='tweets', ignore=[400, 404])

tweets = tweets_collection.find()

id_count = 0
bulk_count = 0
index_every = 10000
tweet_list = []
print(tweets.count())

f = open('./tweet_mapping.yml')
# use safe_load instead load
tweet_mapping = yaml.safe_load(f)
f.close()

print(tweet_mapping)

es.create(index='tweets', doc_type='tweet', id=1, ignore=400, body=tweet_mapping)

for tweet in tweets:
    try:
        id_count += 1
        # bulk_count += 1
        # tweet_list.append(tweet)
        res = es.index(index="tweets", doc_type='tweet', id=id_count, body=dumps(tweet))
        print(id_count)
    except Exception:
        pass
        # if bulk_count > index_every:
        #     bulk_count = 0
        #     helpers.bulk(es, tweet_list)

es.indices.refresh(index="tweets")
