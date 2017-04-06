import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import TweetTokenizer

nltk.download("wordnet", "../venv/nltk_data/")

tknzr = TweetTokenizer()
porter_stemmer = PorterStemmer()
lancaster_stemmer = LancasterStemmer()
wordnet_lemmatizer = WordNetLemmatizer()


tweet = 'RT @yassinedoghri: just a cooool example! :D http://example.com #NLP'
print(tknzr.tokenize(tweet))

for token in tknzr.tokenize(tweet):
    print(porter_stemmer.stem(token))
    print(lancaster_stemmer.stem(token))
    print(wordnet_lemmatizer.lemmatize(token))

# client = MongoClient('localhost', 27017)
# db = client.atlantis_cz4034
# tweets_collection = db.tweets
# parsed_tweets_collection = db.tweets_parsed
#
# cursor = tweets_collection.find()
# i = 0
# for document in cursor:
#     i += 1
#     print(i)
