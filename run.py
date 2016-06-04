#!/usr/bin/env python

import tweepy, time, sys, os, json
from ConfigParser import SafeConfigParser
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# Our name
BOT_NAME = 'updogbot'

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

def parseTweet(tweet):
	handle = '@' + tweet.screen_name
	replyText = handle + ' What\'s updog?'
	api.update_status(status = replyText, in_reply_to_status_id = tweet.tweet_id)

def followUser(tweet):
	api.create_friendship(tweet.screen_name)

# Tweet class with all the information we need for this program (Hashtags and the actual tweet text)
class Tweet:
	text = str()
	hashtags = []
	urls = []
	tweet_id = ''
	screen_name = ''
	user = {}
	full = {}

	def __init__(self, json):
		self.text = json.get('text', '')
		self.hashtags = json.get('entities', {}).get('hashtags', [])
		self.urls = json.get('entities', {}).get('urls', [])
		self.tweet_id = json.get('id', '')

		self.user = json.get('user', {})
		self.screen_name = self.user.get('screen_name', '')

		self.full = json

# Basic listener which parses the json, creates a tweet, and sends it to parseTweet
class TweetListener(StreamListener):
	def on_data(self, data):
		jsonData = json.loads(data)
		tweet = Tweet(jsonData)

		print 'From: @' + tweet.screen_name + ', tweet: ' + tweet.text

		if tweet.screen_name == BOT_NAME:
			return True

		parseTweet(tweet)
		followUser(tweet)
		return True

	def on_error(self, status):
		print status

if __name__ == '__main__':
	listener = TweetListener()
	stream = Stream(auth, listener)	
	stream.filter(track=['updog', 'Updog'])