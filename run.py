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

if __name__ == '__main__':
	listener = TweetListener()
	stream = Stream(auth, listener)	
	stream.filter(track=[BOT_NAME])