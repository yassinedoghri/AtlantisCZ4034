import string
from datetime import datetime, timedelta
from email.utils import parsedate_tz
import operator

from nltk.corpus import stopwords
from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import TweetTokenizer
from pymongo import MongoClient
from tqdm import tqdm

nltk.download("wordnet", "../venv/nltk_data/")
nltk.download("stopwords", "../venv/nltk_data")
nltk.download("vader_lexicon", "../venv/nltk_data")

tknzr = TweetTokenizer()
porter_stemmer = PorterStemmer()
lancaster_stemmer = LancasterStemmer()
wordnet_lemmatizer = WordNetLemmatizer()


#
# tweet = 'RT @yassinedoghri: just a cooool example! :D http://example.com #NLP'
# print(tknzr.tokenize(tweet))


def to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


client = MongoClient('localhost', 27017)
db = client.cz4034
tweets_collection = db.tweets
parsed_tweets_collection = db.tweets_parsed

tweets_cursor = tweets_collection.find()
total_count = tweets_cursor.count()

i = 0
bulk = parsed_tweets_collection.initialize_ordered_bulk_op()
stops = set(stopwords.words("english"))
punctuations = list(string.punctuation)

sid = SentimentIntensityAnalyzer()
for tweet in tqdm(tweets_cursor, total=total_count):
    i += 1
    tweet_text = tweet['text']
    text_tokenized = tknzr.tokenize(tweet_text)
    text_lemmatized = []
    for token in text_tokenized:
        text_lemmatized.append(wordnet_lemmatizer.lemmatize(token))
    text_tokenized_nsw = [word for word in text_tokenized if word not in stops]
    text_tokenized_np = [i for i in text_tokenized if i not in punctuations]

    tweet['created_at'] = to_datetime(tweet['created_at'])
    tweet['user']['created_at'] = to_datetime(tweet['user']['created_at'])
    tweet['text_tokenized'] = text_tokenized
    tweet['text_tokenized_nsw'] = text_tokenized_nsw
    tweet['text_tokenized_np'] = text_tokenized_np
    tweet['text_lemmatized'] = text_lemmatized

    ss = sid.polarity_scores(tweet_text)
    tweet['sentiment'] = ss
    del ss['compound']
    if ss['neu'] < 0.8:
        del ss['neu']
    tweet['leading_sentiment'] = max(ss.items(), key=operator.itemgetter(1))[0]  # neg, neu, pos

    bulk.find({'_id': tweet['_id']}).upsert().update({'$set': tweet})
    if i >= 10000:
        i = 0
        bulk.execute()
        bulk = parsed_tweets_collection.initialize_ordered_bulk_op()
if i > 0:
    bulk.execute()
