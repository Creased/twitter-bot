#!/usr/bin/env python
# -*- coding:Utf-8 -*-

#==========================================================#
# [+] Title:   Twitter bot                                 #
# [+] Author:  Baptiste M. (Creased)                       #
# [+] Website: bmoine.fr                                   #
# [+] Email:   contact@bmoine.fr                           #
# [+] Twitter: @Creased_                                   #
#==========================================================#

import os
import sys
import json
import time
import tweepy
import argparse

from modules import log
from modules.sleep import timeSleep

#
# Variables
#

__version__ = '0.1-dev'
sleep       = timeSleep()

#
# Functions
#

def handleRequest(callback):
    while True:
        try:
            yield callback.next()
        except tweepy.error.TweepError as e:
            if e.response is not None and e.response.status_code in set([429]):
                sleep.sleepWindow()
            else:
                # log.debug(e.response.__dict__)
                log.debug(e.__dict__)
        break

def loadConfig(conf):
    log.success('Loading configurations from {file}'.format(file=args.config))
    config = dict()

    if conf:
        try:
            with open(conf, 'rt') as conf_fd:
                config = json.load(conf_fd)
        except FileNotFoundError as e:
            log.error('Specified configuration file not found')
            sys.exit(1)
        except Exception as e:
            log.error('An error occured while parsing configuration file')
            sys.exit(1)

    return config

def likeTweets(api, tweets):
    log.success('Adding gathered tweets to favorites')

    for tweet in tweets:
        try:
            result = api.create_favorite(tweet['id_str'])
        except tweepy.error.TweepError as e:  # Already favorited
            if e.response is not None and e.response.status_code in set([429]):
                sleep.sleepWindow()
            elif not e.api_code or (e.api_code and e.api_code not in set([139])):
                # log.debug(e.response.__dict__)
                log.debug(e)

            continue

        sleep.sleepInterval()  # Sleep to prevent API rate limit

def searchTweets(api, term, limit=100, display=True):
    log.success('Gathering {count} tweet{s} containing \'{term}\''.format(count=limit, s='' if limit == 1 else 's', term=term))

    result = handleRequest(tweepy.Cursor(api.search, q=term).items(limit))
    tweets = []

    if result:
        for tweet in result:
            tweets += [{'id_str': tweet.id_str, 'text': tweet.text}]

        count = len(tweets)
        log.bold('{count} tweet{s} containing \'{term}\''.format(count=count, s='' if count == 1 else 's', term=term))

        if display:
            for tweet in tweets:
                log.info('{tweet}'.format(tweet=tweet['text']))

    sleep.sleepInterval()  # Sleep to prevent API rate limit
    return tweets

def getFavorites(api, limit=100, display=True):
    log.success('Gathering favorites')

    result = handleRequest(tweepy.Cursor(api.favorites).items(limit))
    tweets = []

    if result:
        for tweet in result:
            tweets += [{'id_str': tweet.id_str, 'text': tweet.text}]

        count = len(tweets)
        log.bold('{count} tweet{s}'.format(count=count, s='' if count == 1 else 's'))

        if display:
            for tweet in tweets:
                log.info('{tweet}'.format(tweet=tweet['text']))

    sleep.sleepInterval()  # Sleep to prevent API rate limit
    return tweets

def getFollowers(api, limit=100, display=True):
    log.success('Gathering followers')

    result = handleRequest(tweepy.Cursor(api.followers).items(limit))
    users = []

    if result:
        for user in result:
            users += [{'id_str': user.id_str, 'screen_name': user.screen_name}]

        count = len(users)
        log.bold('{count} user{s}'.format(count=count, s='' if count == 1 else 's'))

        if display:
            for user in users:
                log.info('@{name}'.format(name=user['screen_name']))

    sleep.sleepInterval()  # Sleep to prevent API rate limit
    return users

def getHomeTimeline(api, limit=100, display=True):
    log.success('Gathering home timeline')

    result = handleRequest(tweepy.Cursor(api.home_timeline).items(limit))
    tweets = []

    if result:
        for tweet in result:
            tweets += [{'id_str': tweet.id_str, 'text': tweet.text}]

        count = len(tweets)
        log.bold('{count} tweet{s}'.format(count=count, s='' if count == 1 else 's'))

        if display:
            for tweet in tweets:
                log.info('{tweet}'.format(tweet=tweet['text']))

    sleep.sleepInterval()  # Sleep to prevent API rate limit
    return tweets

def main(args):
    # Load configurations
    config = loadConfig(args.config)

    sleep.interval = config['request_interval']
    sleep.window = config['request_window']

    # Twitter OAuth Authentication
    log.success('Authenticating on Twitter API')
    twitter_auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
    twitter_auth.set_access_token(config['access_token'], config['access_token_secret'])

    # Initialize Twitter API
    twitter_api = tweepy.API(twitter_auth)

    # Search for tweets containing terms from config file
    for term in config['terms']:
        tweets = searchTweets(twitter_api, term, config['tweets_count'], False)
        likeTweets(twitter_api, tweets)  # Add gathered tweets to favorites

    # Show favorites
    getFavorites(twitter_api, 0, False)
#
# Main
#

if '__main__' in __name__:
    try:
        # Arguments parsing
        parser = argparse.ArgumentParser(
            description='Simple Twitter Bot v{version} (sources: git.bmoine.fr/twitter-bot)'.format(version=__version__),
            epilog='Make your Twitter great again!'
        )

        parser.add_argument('-c', '--config', type=str, default='config.json',
                            help='path to JSON configuration file')

        args = parser.parse_args()

        main(args)
    except tweepy.error.TweepError as e:
        log.error('Twitter error: {error}'.format(error=e))
    except Exception as e:
        log.error('An error occured: {error}'.format(error=e))

