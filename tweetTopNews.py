#!/usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser
from bs4 import BeautifulSoup
import tweepy
import time
import sys
import datetime

log = "*********************************************************\n"
now = datetime.datetime.now()
log += "%d-%d-%d %d:%d:%d" % (now.day, now.month, now.year, now.hour, now.minute, now.second)

#Twitter Setup
CONSUMER_KEY = ''  # Enter your own twitter API keys here
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
config = api.configuration() #Get twitter configuration to know the max length of t.co links

#Retrieve RSS feed - Top 24h posts from multi-subreddit topnews
rss_feed_url = "https://www.reddit.com/user/#/m/topnews/.rss?sort=top&t=day"  # Replace '#' with your reddit username
feed = feedparser.parse(rss_feed_url)

#Function to create tweet, check length, truncate title if necessary
def createTweet(title,link,config):
    tweet = ""
    max_url_length = len(link)
    if len(link)>config['short_url_length_https']:
        max_url_length = config['short_url_length_https']
    if len(title)+len("\n")+max_url_length>140:
        to_cut = len(title)+len("\n")+max_url_length-138
        title = title[:-to_cut]
        title += "… "
    tweet += title + "\n" + link
    return tweet

#Create list with the top 10 tweets
tweets = []
error = ""

for i in range(0,10):
    try:
        title = feed.entries[i].title
        soup = BeautifulSoup(feed.entries[i].summary, "html5lib")
        for link in soup.findAll('a', href=True, text='[link]'):
            link = link['href']
        tweets.append(createTweet(title, link, config))
    except Exception as e:
        error = "<p>Error: %s</p>" % e
        log += "\n" + error
        pass

#Publish tweets
for t in tweets:
    try:
        api.update_status(t)
        time.sleep(5)
    except Exception as e:
        error = "<p>Error: %s</p>" % e
        log += "\n" + error
        pass

#Write log file
log += "\n" + "End of this publication.\n"
with open("log.txt","a") as f:
    f.write(log)

#Print confirmation
print("Great success!")
