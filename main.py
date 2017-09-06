#!/usr/bin/env python
# -*- coding:Utf-8 -*-

"""Simple Twitter Bot."""

#==========================================================#
# [+] Title:   Twitter bot                                 #
# [+] Author:  Baptiste M. (Creased)                       #
# [+] Website: bmoine.fr                                   #
# [+] Email:   contact@bmoine.fr                           #
# [+] Twitter: @Creased_                                   #
#==========================================================#

__version__ = '0.1-dev'

import sys
import json
import argparse
import tweepy

from modules import log
from modules.sleep import TimeSleep

#
# Functions
#

def handle_request(callback):
    """Process request to Twitter API."""
    while True:
        try:
            return callback
        except tweepy.error.TweepError as e:
            if e.response is not None and e.response.status_code in set([429]):
                sleep.sleep_window()
            else:
                # log.debug(e.response.__dict__)
                log.debug(e.__dict__)
        break

def load_config(conf):
    """Load configuration from file."""
    log.success('Loading configurations from {file}'.format(file=conf))
    config = dict()

    if conf:
        try:
            with open(conf, 'rt') as conf_fd:
                config = json.load(conf_fd)
        except FileNotFoundError:
            log.error('Specified configuration file not found')
            sys.exit(1)
        except Exception:
            log.error('An error occured while parsing configuration file')
            sys.exit(1)

    return config

def like_tweets(api, tweets):
    """Add specified tweets to favorites."""
    log.success('Adding gathered tweets to favorites')

    for tweet in tweets:
        try:
            result = api.create_favorite(tweet['id_str'])
        except tweepy.error.TweepError as e:  # Already favorited
            if e.response is not None and e.response.status_code in set([429]):
                sleep.sleep_window()
            elif not e.api_code or (e.api_code and e.api_code not in set([139])):
                # log.debug(e.response.__dict__)
                log.debug(e)

            continue

        sleep.sleep_interval()  # Sleep to prevent API rate limit

    return result

def search_tweets(api, term, limit=100, display=True):
    """Search for tweets containing specified term."""
    log.success('Gathering {count} tweet{s} containing \'{term}\''.format(
        count=limit,
        s='' if limit == 1 else 's',
        term=term
    ))

    result = handle_request(tweepy.Cursor(api.search, q=term).items(limit))
    tweets = []

    if result:
        for tweet in result:
            tweets += [{
                'id_str': tweet.id_str,
                'text': tweet.text
            }]

        count = len(tweets)
        log.bold('{count} tweet{s} containing \'{term}\''.format(
            count=count,
            s='' if count == 1 else 's',
            term=term
        ))

        if display:
            for tweet in tweets:
                log.info('{tweet}'.format(tweet=tweet['text']))

    sleep.sleep_interval()  # Sleep to prevent API rate limit
    return tweets

def get_favorites(api, limit=100, display=True):
    """Get tweets from favorites."""
    log.success('Gathering favorites')

    result = handle_request(tweepy.Cursor(api.favorites).items(limit))
    tweets = []

    if result:
        for tweet in result:
            tweets += [{
                'id_str': tweet.id_str,
                'text': tweet.text
            }]

        count = len(tweets)
        log.bold('{count} tweet{s}'.format(
            count=count,
            s='' if count == 1 else 's'
        ))

        if display:
            for tweet in tweets:
                log.info('{tweet}'.format(tweet=tweet['text']))

    sleep.sleep_interval()  # Sleep to prevent API rate limit
    return tweets

def get_followers(api, limit=100, display=True):
    """Get followers list."""
    log.success('Gathering followers')

    result = handle_request(tweepy.Cursor(api.followers).items(limit))
    users = []

    if result:
        for user in result:
            users += [{
                'id_str': user.id_str,
                'screen_name': user.screen_name
            }]

        count = len(users)
        log.bold('{count} user{s}'.format(
            count=count,
            s='' if count == 1 else 's'
        ))

        if display:
            for user in users:
                log.info('@{name}'.format(name=user['screen_name']))

    sleep.sleep_interval()  # Sleep to prevent API rate limit
    return users

def get_home_timeline(api, limit=100, display=True):
    """Get home timeline."""
    log.success('Gathering home timeline')

    result = handle_request(tweepy.Cursor(api.home_timeline).items(limit))
    tweets = []

    if result:
        for tweet in result:
            tweets += [{
                'id_str': tweet.id_str,
                'text': tweet.text
            }]

        count = len(tweets)
        log.bold('{count} tweet{s}'.format(
            count=count,
            s='' if count == 1 else 's'
        ))

        if display:
            for tweet in tweets:
                log.info('{tweet}'.format(tweet=tweet['text']))

    sleep.sleep_interval()  # Sleep to prevent API rate limit
    return tweets

def main(args):
    """Bot main function."""
    # Load configurations
    config = load_config(args.config)

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
        tweets = search_tweets(twitter_api, term, config['tweets_count'], False)
        like_tweets(twitter_api, tweets)  # Add gathered tweets to favorites

    # Show favorites
    get_favorites(twitter_api, 0, False)
#
# Main
#

if __name__ == '__main__':
    try:
        sleep = TimeSleep()

        # Arguments parsing
        parser = argparse.ArgumentParser(
            description='Simple Twitter Bot v{version} (sources: git.bmoine.fr/twitter-bot)'.format(
                version=__version__
            ),
            epilog='Make your Twitter great again!'
        )

        parser.add_argument('-c', '--config',
                            type=str,
                            default='config.json',
                            help='path to JSON configuration file')

        main(parser.parse_args())
    except tweepy.error.TweepError as e:
        log.error('Twitter error: {error}'.format(error=e))
    except Exception as e:
        log.error('An error occured: {error}'.format(error=e))
