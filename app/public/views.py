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
    page = int(request.args.get('page', default=1))
    size = int(request.args.get('size', default=10))
    previous_page = page - 1
    next_page = page + 1
    query = None
    if request.method == 'GET':
        query = request.args.get('q')
    # perform search
    res = es_search(query, page, size)
    number_of_pages = math.ceil(res['hits']['total'] / size)
    number_of_docs = len(res['hits']['hits'])
    return render_template('public/index.html',
                           tweets=res,
                           prev_page=previous_page,
                           curr_page=page,
                           next_page=next_page,
                           number_of_pages=number_of_pages,
                           page_list=get_pages(page, number_of_pages),
                           number_of_docs=number_of_docs)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')


def es_search(query=None, page=1, size=10):
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
                            "factor": 0.00001
                        },
                        "weight": 10
                    },
                    {
                        "field_value_factor": {
                            "field": "favorite_count",
                            "missing": 1,
                            "factor": 0.00001
                        },
                        "weight": 10
                    }
                ],
                "boost_mode": "multiply",
                "score_mode": "multiply"
            }
        }
    }
    if query is not None:
        es_query['query']['function_score']['query'] = {
            "query_string": {
                "query": query,
                "fields": ["text"]
            }
        }
    es_query["from"] = (page - 1) * size
    es_query["size"] = size
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
