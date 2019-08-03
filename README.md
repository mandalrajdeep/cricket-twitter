# Twitter Data Clustering

Collect and cluster tweets about the game of cricket around various important events of the game (toss, wicket, boundaries, drinks, powerplay, catch, sixes, fours etc.) and arrange these in a time series to summarise a game's progress.

## Getting Started

With the absence of any significant cricket or any event (sporting or nonsporting), it was difficult to gather data for writing an event-based clustering program. In the meantime, I picked up a trending hashtag on Twitter and captured all tweets for a day. Using this data, detecting events did not make much sense, so the program only clusters data into different categories. 

## Input Charachteristics

* Total Tweets - 40,556
* Total Tokens - 483,034
* Unique Significant Tokens - 6110
* Clusters - 10 (Randomly Set)

## Clusters
What things you need to install the software and how to install them

```
8 ... 24664
9 ... 5327
7 ... 3970
0 ... 2424
6 ... 1222
2 ... 772
1 ... 731
4 ... 602
3 ... 522
5 ... 322
```

## Programming

This is accomplished through Twitter’s API - tweets are read live and stored into a MongoDB database.

## Tweet Consumer
The program processes the collection containing all the streamed tweets, performing the following operations:
1. Read tweets from Mongo DB collection
2. Perform tokenization and stemming of tweets 
3. Convert each tweet into a TF/IDF vector
4. Perform K Means Clustering
5. Store Clustered Timeline Data in File

## Live Cricket Streaming

If a cricket match would have been going on, it would surely have got more interesting. While broadly, clustering would happen in a fashion similar to the above problem, there will be quite a few different aspects.

## Cluster Based Events

The clustering of the tweets would be based on lexicon based event recognition. Each lexicon will stand for a particular event, like a wicket, boundary, six etc. 


```
Eg. Boundary = [‘boundary’, ‘four’, ‘4’], Wicket = [‘catch’, ‘out’, ‘bowled’, ‘stumped’, ‘lbw’, ‘wicket’]
```

We have not created these defined lexicons in our solution, as there was no event to track as such. However, in a cricket match live feed, these lexicons will help us directly cluster our tweets, and we wouldn’t require a computational TF/IDF vector clustering. The advantage here is that, no training data will be required for this, any incoming tweet can easily be evaluated.

In order to improve upon this, lexicons can be introduced for players as well.

```
Eg. Rahul Dravid = [‘rahul’, ‘dravid’, ‘wall’]
```

Together with an event lexicon, it can describe an event with the players involved. In our timeline, each cluster detected would be one point on the timeline, i.e. one event on the timeline. In the current case, there is no such cluster based timeline, it is just a series of time sorted tweets within each cluster.

## Event Triggers

An event trigger needs to be defined to identify relevant events in the game. This is essential as a cricket match initiates a lot of tweets commenting on various aspects of the game, but are unlikely to give us any information. Intuitively, an event will trigger when there is a sudden burst of tweets. 

We can generally process tweets in the previous one minute at all times, and whenever there is a sudden jump in the number of tweets in the second half of the time window over the first half, we can declare an event, and move on to process the tweets. If there is no trigger, the tweets in the time window need not be processed.

```
(tweets in the first 30 seconds/tweets in the next 30 seconds)>2 (threshold)
```

### Prevent Event Duplicates


With a huge chunk of data coming in, event duplicates are likely in our method. This can be reduced by ignoring all retweets.

