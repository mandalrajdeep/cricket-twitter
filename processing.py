# this is a tweet processor and performs the following operations
# 1. reads tweets from the mongo database
# 2. analyses the tweets by removing noise
# 3. creates a vector out of the tweets
# 4. performs k-means clustering to segregate data in different clusters

import re
from collections import Counter
import operator 
import time
from pymongo import MongoClient
from nltk.corpus import stopwords
import string
from nltk.collocations import *
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
import pandas as pd
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.externals import joblib

#declare outfile file name
OUTPUT_FILENAME = 'Tweets_Timeline.csv'

#declare input database
MONGO_HOST= 'mongodb://localhost/tweets'

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
    
# initialise all global variables

# variables for tweet tokenization and stemming
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation + ['rt', 'via']
stemmer = SnowballStemmer("english")
totalvocab_stemmed = []
totalvocab_tokenized = []

# list to keep post processed tweets
cleaned_tweets = []

# list to keep semi processed tweets
full_tweets =[]

# list to keep tweet creation times
tweet_times = []

# declare the number of clusters for K Means
num_clusters = 10
km = KMeans(n_clusters=num_clusters)

# list array to store dominating words in each cluster
top_words = [[] for i in range(num_clusters)]

def tokenize(s):
   return tokens_re.findall(s)
 
def tokenize_and_stem(s, lowercase=True):
   tokens = tokenize(s)
   if lowercase:
      tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
      stems = [stemmer.stem(t) for t in tokens]
   return stems
 
def tokenize_only(s, lowercase=True):
   tokens = tokenize(s)
   if lowercase:
      tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
   return tokens

# vector config variable
tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                 min_df=0.0005, stop_words='english',
                                 use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))

try:
   # connect and download from DB
   client = MongoClient(MONGO_HOST)
   db = client.tweets
   collection = db.twitter_search.find({"quote_count": 0}, {"created_at": 1, "text": 1, 'reply_count':1, 'favorite_count':1})

   for pretweet in collection:
      # process each tweet
      tweet = pretweet['text'].encode('ascii', 'ignore').decode('ascii').lower().replace('rt', '').replace('amp', '')
      full_tweet = re.sub(r'\s+', ' ', tweet)
      ' '.join( [w for w in tweet.split() if len(w)>1] )
      tweet = re.sub(r'[^A-Za-z0-9@#]+', ' ', tweet)
      created_at = pretweet['created_at']

      allwords_stemmed = tokenize_and_stem(tweet) #for each item in 'synopses', tokenize/stem
      totalvocab_stemmed.extend(allwords_stemmed) #extend the 'totalvocab_stemmed' list
      
      allwords_tokenized = tokenize_only(tweet)
      totalvocab_tokenized.extend(allwords_tokenized)

      full_tweets.append(full_tweet)
      cleaned_tweets.append(tweet)
      tweet_times.append(created_at)

except Exception as e:
   print('Err ',e)

# store all tokenized words in a dataframe
vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index = totalvocab_stemmed)
print ('There are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')

# define vectorizer parameters
tfidf_matrix = tfidf_vectorizer.fit_transform(cleaned_tweets) #fit the vectorizer to synopsis
print(tfidf_matrix.shape)
terms = tfidf_vectorizer.get_feature_names()

# performing k means
km.fit(tfidf_matrix)
clusters = km.labels_.tolist()
print('Tweets Count: ' + str(len(clusters)))

#joblib.dump(km, 'doc_cluster.pkl')
#km = joblib.load('doc_cluster.pkl')

twitter_feed = { 'cluster': clusters, 'created_at': tweet_times, 'text': full_tweets }

frame = pd.DataFrame(twitter_feed, index = [clusters] , columns = ['cluster','text', 'created_at'])
print(frame['cluster'].value_counts()) #number of films per cluster (clusters from 0 to 4)
frame = frame.sort_values(['cluster', 'created_at'], ascending=[True,True])


# print most popular words in each cluster
# sort cluster centers by proximity to centroid
order_centroids = km.cluster_centers_.argsort()[:, ::-1] 
for i in range(num_clusters):
   for ind in order_centroids[i, :10]: 
      word = vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore')
      top_words[i].append(word)
   print('Cluster ' + str(i) + ' Top Words:')
   print(list(set(top_words[i])))

# Write Dataframe to File
frame.to_csv(OUTPUT_FILENAME)


