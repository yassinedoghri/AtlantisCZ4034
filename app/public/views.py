# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, render_template, request
import pymongo
from elasticsearch import Elasticsearch
import math

es = Elasticsearch()

blueprint = Blueprint('public', __name__, static_folder='../static')

client = pymongo.MongoClient('localhost', 27017)
db = client.cz4034
tweets_collection = db.tweets
parsed_tweets_collection = db.tweets_parsed

tweets_collection.ensure_index([('id', pymongo.ASCENDING)])
tweets_collection.ensure_index([('created_at', pymongo.ASCENDING)])
tweets_collection.ensure_index([('retweeted', pymongo.ASCENDING)])


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    page = int(check_param('page', default=1))
    size = int(check_param('size', default=10))
    date_from = check_param('tweets_from', default='')
    date_to = check_param('tweets_to', default='')
    sentiment = {
        'neg': int(check_param('neg', default=0)),
        'neu': int(check_param('neu', default=0)),
        'pos': int(check_param('pos', default=0))
    }
    previous_page = page - 1
    next_page = page + 1
    query = check_param('q', default='')
    # perform search
    res = es_search(query, page, size, date_from, date_to, sentiment)
    number_of_pages = math.ceil(res['hits']['total'] / size)
    number_of_docs = len(res['hits']['hits'])
    sentiments_data = parse_buckets(res['aggregations']['sentiments']['buckets'])
    sentiment_over_time = parse_sentiment_over_time(res['aggregations']['sentiment_over_time']['buckets'])
    return render_template(
        'public/index.html',
        tweets=res,
        query=query,
        prev_page=previous_page,
        curr_page=page,
        next_page=next_page,
        number_of_pages=number_of_pages,
        page_list=get_pages(page, number_of_pages),
        number_of_docs=number_of_docs,
        tweets_from=date_from,
        tweets_to=date_to,
        sentiment=sentiment,
        sentiments_data=sentiments_data,
        sentiment_over_time=sentiment_over_time
    )


def check_param(name, default):
    param = request.args.get(name)
    return param if param else default


def parse_buckets(bucket_list):
    bucket_dict = {}
    for bucket in bucket_list:
        bucket_dict[bucket['key']] = bucket['doc_count']
    return bucket_dict


def parse_sentiment_over_time(bucket_list):
    labels = []
    line_dataset = []
    bar_dataset = []
    neg_data = []
    neu_data = []
    pos_data = []
    for bucket in bucket_list:
        labels.append(bucket['key_as_string'])
        line_dataset.append(bucket['doc_count'])
        neg_data.append(get_sentiment_count(bucket, 'neg'))
        neu_data.append(get_sentiment_count(bucket, 'neu'))
        pos_data.append(get_sentiment_count(bucket, 'pos'))
    bar_dataset = [
        {
            "label": "Negative",
            "backgroundColor": "#FF6384",
            "data": neg_data,
            "stack": 1
        },
        {
            "label": "Positive",
            "backgroundColor": "#36A2EB",
            "data": pos_data,
            "stack": 1
        },
        {
            "label": "Neutral",
            "backgroundColor": "#CCCCCC",
            "data": neu_data,
            "stack": 1
        }
    ]
    data = {
        'labels': labels,
        'datasets': bar_dataset
    }
    print(data)
    return data


def get_sentiment_count(bucket_list, key=''):
    for bucket in bucket_list['count_by_sentiment']['buckets']:
        if bucket['key'] == key:
            return bucket['doc_count']
    return 0


@blueprint.route('/tweet_search/', methods=['GET', 'POST'])
def tweet_search():
    """Tweet Search page."""
    page = int(check_param('page', default=1))
    size = int(check_param('size', default=10))
    date_from = check_param('tweets_from', default='')
    date_to = check_param('tweets_to', default='')
    sentiment = {
        'neg': int(check_param('neg', default=0)),
        'neu': int(check_param('neu', default=0)),
        'pos': int(check_param('pos', default=0))
    }
    next_page = page + 1
    query = check_param('q', default='')
    # perform search
    res = es_search(query, page, size, date_from, date_to, sentiment)
    return render_template('public/tweet_search.html',
                           tweets=res,
                           query=query,
                           next_page=next_page)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')


def es_search(query=None, page=1, size=10, date_from=None, date_to=None, sentiment=None):
    es_query = {
        "query": {
            "function_score": {
                "query": {
                    "match_all": {}
                },
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "retweet_count",
                            "missing": 1,
                            "factor": 0.0001,
                            "modifier": "log1p"
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "favorite_count",
                            "missing": 1,
                            "factor": 0.0001,
                            "modifier": "log1p"
                        }
                    }
                ],
                "boost_mode": "multiply",
                "score_mode": "multiply",
                "filter": {"bool": {"must": []}},
            }
        },
        "from": (page - 1) * size,
        "size": size,
        "aggregations": {
            "sentiments": {
                "terms": {"field": "leading_sentiment"}
            },
            "sentiment_over_time": {
                "date_histogram": {
                    "field": "created_at",
                    "interval": "day",
                    "format": "dd-MM-yyyy"
                },
                "aggs": {
                    "count_by_sentiment": {
                        "terms": {
                            "field": "leading_sentiment"
                        }
                    }
                }
            }
        }
    }
    if query:
        es_query['query']['function_score']['query'] = {
            "query_string": {
                "query": query,
                "fields": ["text^2"]
            }
        }
    if date_from or date_to:
        date_filter = {
            "range": {
                "created_at": {
                    "lte": date_to if date_to else "now",
                    "format": "dd-MM-yyyy||yyyy"
                }
            }
        }
        if date_from:
            date_filter["range"]["created_at"]["gte"] = date_from
        es_query['query']["function_score"]["filter"]["bool"]["must"].append(date_filter)
    if any(v > 0 for k, v in sentiment.items()):
        sentiment_filter = {
            "terms": {"leading_sentiment": [k for k, v in sentiment.items() if v > 0]}
        }
        es_query['query']["function_score"]["filter"]["bool"]["must"].append(sentiment_filter)
    print(es_query)
    res = es.search(index="tweets", body=es_query)
    print(res)
    return res


def get_pages(curr_page, number_of_pages, pages_to_show=5):
    page_list = []
    start = 1 if pages_to_show >= curr_page else curr_page - pages_to_show + 1
    end = pages_to_show + 1 if pages_to_show >= curr_page else curr_page + 1
    if curr_page > pages_to_show + 1:
        page_list.append({
            "num": 1,
            "class": ''
        })
        page_list.append({
            "num": ''
        })
    for i in range(start, end):
        page_obj = {
            "num": i,
            "class": 'active' if i == curr_page else ''
        }
        page_list.append(page_obj)
    if curr_page < number_of_pages - 1:
        page_list.append({
            "num": ''
        })
        page_list.append({
            "num": number_of_pages,
            "class": ''
        })
    return page_list
