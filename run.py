#!/usr/bin/env python

import tweepy, time, sys, os, json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# Our name
BOT_NAME = '@updogbot'

TWITTER_LIMIT = 140

parser = SafeConfigParser()
parser.read('secrets.cfg')

# Twitter credentials
CONSUMER_KEY = parser.get('Twitter', 'CONSUMER_KEY')
CONSUMER_SECRET = parser.get('Twitter', 'CONSUMER_SECRET')
ACCESS_KEY = parser.get('Twitter', 'ACCESS_KEY')
ACCESS_SECRET = parser.get('Twitter', 'ACCESS_SECRET')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)


# Tweet class with all the information we need for this program (Hashtags and the actual tweet text)
class Tweet:
	text = str()
	hashtags = []
	urls = []
	full = {}

	def __init__(self, json):
		self.text = json.get('text', '')
		self.hashtags = json.get('entities', {}).get('hashtags', [])
		self.urls = json.get('entities', {}).get('urls', [])
		self.full = json

# Basic listener which parses the json, creates a tweet, and sends it to parseTweet
class TweetListener(StreamListener):
	def on_data(self, data):
		jsonData = json.loads(data)
		tweet = Tweet(jsonData)
		parseTweet(tweet)
		return True

	def on_error(self, status):
		print status

if __name__ == '__main__':
	listener = TweetListener()
	stream = Stream(auth, listener)	
	stream.filter(track=['updog'])