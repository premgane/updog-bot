#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tweepy, time, sys, os, json
from random import randint
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

EMOJI_RESPONSE_ARRAY = ['🤔', '🐶', '🐕', '🐩', '🐺', '🐾']
DEFAULT_RESPONSE = 'What\'s updog?'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# To ensure some rate limiting
MIN_SECS_BETWEEN_RESPONSES = 30
lastResponseTimestamp = time.time()

# Keep track of the latest people we've responded to
CIRCULAR_ARRAY_MAX_CAPACITY = 10
circularArrayOfHandles = [''] * CIRCULAR_ARRAY_MAX_CAPACITY
circularArrayPointer = 0

# Ensure the given object is a str, not a unicode object
def unicodeToStr(s):
	if isinstance(s, unicode):
		s = str(s)
	return s

# Posts a response tweet
def respond(tweet):
	global lastResponseTimestamp
	global circularArrayPointer
	if time.time() - lastResponseTimestamp < MIN_SECS_BETWEEN_RESPONSES:
		return

	lastResponseTimestamp = time.time()

	handle = '@' + tweet.screen_name
	replyText = handle + ' '

	if BOT_NAME in tweet.text.lower() or 'updog bot' in tweet.text.lower() or handle in circularArrayOfHandles:
		replyText = replyText + EMOJI_RESPONSE_ARRAY[randint(0, len(EMOJI_RESPONSE_ARRAY))]
	else:
		replyText = replyText + DEFAULT_RESPONSE

	# Insert handle into our list of handles we've last responded to
	if not handle in circularArrayOfHandles:
		circularArrayOfHandles[circularArrayPointer] = handle
		circularArrayPointer = circularArrayPointer + 1
		if circularArrayPointer >= CIRCULAR_ARRAY_MAX_CAPACITY:
			circularArrayPointer = 0
	
	print circularArrayOfHandles

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

# Determines whether we should retweet a given tweet or not
def shouldRetweet(tweet):
	if BOT_NAME in tweet.text.lower() or 'updog bot' in tweet.text.lower():
		return False

	if tweet.full.get('quoted_status', {}).get('user', {}).get('screen_name', '') == BOT_NAME:
		return False

	return True

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

		print '@' + tweet.screen_name.encode("utf-8") + ': ' + tweet.text.encode("utf-8")

		# Ignore the tweet if it's us or if we think the tweeter is a bot
		if BOT_NAME in tweet.screen_name or 'bot' in tweet.screen_name.lower():
			return True

		if not str.startswith(tweet.text, 'RT '):
			respond(tweet)
		
		if shouldRetweet(tweet):
			retweet(tweet)
		
		followUser(tweet)
		return True

	def on_error(self, status):
		print status

if __name__ == '__main__':
	listener = TweetListener()
	stream = Stream(auth, listener)	
	stream.filter(track=['updog', 'Updog'])