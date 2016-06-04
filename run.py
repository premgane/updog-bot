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

def unicodeToStr(s):
	if isinstance(s, unicode):
		s = str(s)
	return s

# Posts a response tweet
def respond(tweet):
	handle = '@' + tweet.screen_name
	replyText = handle + ' What\'s updog?'
	api.update_status(status = replyText, in_reply_to_status_id = tweet.tweet_id)

# RTs the given tweet
def retweet(tweet):
	try:
		api.retweet(tweet.tweet_id)
	except tweepy.error.TweepError as err:
		print("RTing, Tweepy error: {0}".format(err))

# Follows the user who posted the given tweet
def followUser(tweet):
	try:
		api.create_friendship(tweet.screen_name)
	except tweepy.error.TweepError as err:
		print("Following user, Tweepy error: {0}".format(err))

# Tweet class with some attributes and the full JSON itself
class Tweet:
	text = str()
	hashtags = []
	urls = []
	tweet_id = ''
	screen_name = ''
	user = {}
	full = {}

	def __init__(self, json):
		self.text = unicodeToStr(json.get('text', ''))
		self.hashtags = json.get('entities', {}).get('hashtags', [])
		self.urls = json.get('entities', {}).get('urls', [])
		self.tweet_id = unicodeToStr(json.get('id', ''))

		self.user = json.get('user', {})
		self.screen_name = unicodeToStr(self.user.get('screen_name', ''))

		self.full = json

# Basic listener: parse the tweet, respond if appropriate, RT if appropriate, and follow the user
class TweetListener(StreamListener):
	def on_data(self, data):
		jsonData = json.loads(data)
		tweet = Tweet(jsonData)

		print 'From: @' + tweet.screen_name.encode("utf-8") + ', tweet: ' + tweet.text.encode("utf-8")

		if tweet.screen_name == BOT_NAME:
			return True

		if not str.startswith(tweet.text, 'RT '):
			respond(tweet)
		
		retweet(tweet)
		
		followUser(tweet)
		return True

	def on_error(self, status):
		print status

if __name__ == '__main__':
	listener = TweetListener()
	stream = Stream(auth, listener)	
	stream.filter(track=['updog', 'Updog'])