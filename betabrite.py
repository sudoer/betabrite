#!/usr/bin/python
# -*- coding: utf8 -*-

import serial
import datetime
import random
import time
import ConfigParser
import tweepy
import sys
import re
import os
from pprint import pprint
import urllib

# GLOBALS

ledSerialPort = None
twitterApi = None
class preferences:
    pass

#-------------------------------------------------------------------------------
#   T W I T T E R   S T U F F
#-------------------------------------------------------------------------------

def twitterInit():
    global twitterApi
    global preferences
    config = ConfigParser.RawConfigParser()
    config.read('settings.cfg')
    # http://dev.twitter.com/apps/myappid
    # http://dev.twitter.com/apps/myappid/my_token
    CONSUMER_KEY = config.get('Twitter OAuth', 'CONSUMER_KEY')
    CONSUMER_SECRET = config.get('Twitter OAuth', 'CONSUMER_SECRET')
    ACCESS_TOKEN_KEY = config.get('Twitter OAuth', 'ACCESS_TOKEN_KEY')
    ACCESS_TOKEN_SECRET = config.get('Twitter OAuth', 'ACCESS_TOKEN_SECRET')
    preferences.TWITTER_USER = config.get('preferences', 'TWITTER_USER')
    preferences.MY_TWEETS = config.get('preferences', 'MY_TWEETS')
    preferences.OTHER_TWEETS = config.get('preferences', 'OTHER_TWEETS')

    twitterAuth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    twitterAuth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    twitterApi = tweepy.API(twitterAuth, secure=True)

def twitterGetUserTweets(i):
    global twitterApi
    global preferences
    twitterUserObj = twitterApi.get_user(preferences.TWITTER_USER)
    return twitterApi.user_timeline(screen_name=twitterUserObj, include_rts=True, count=i)

def twitterGetHomeTweets(i):
    global twitterApi
    global preferences
    twitterUserObj = twitterApi.get_user(preferences.TWITTER_USER)
    return  twitterApi.home_timeline(screen_name=twitterUserObj, include_rts=True, count=i)

    # Display basic details for twitter user name
    ## print (" ")
    ## print ("Basic information for", twitterUserObj.name)
    ## print ("Screen Name:", twitterUserObj.screen_name)
    ## print ("Name: ", twitterUserObj.name)
    ## print ("Twitter Unique ID: ", twitterUserObj.id)
    ## print ("Account created at: ", twitterUserObj.created_at)

        # print ("ID:", tweet.id)
        # print ("User ID:", tweet.user.id)
        # print ("Text:", tweet.text)
        # print ("Created:", tweet.created_at)
        # print ("Geo:", tweet.geo)
        # print ("Contributors:", tweet.contributors)
        # print ("Coordinates:", tweet.coordinates)
        # print ("Favorited:", tweet.favorited)
        # print ("In reply to screen name:", tweet.in_reply_to_screen_name)
        # print ("In reply to status ID:", tweet.in_reply_to_status_id)
        # print ("In reply to status ID str:", tweet.in_reply_to_status_id_str)
        # print ("In reply to user ID:", tweet.in_reply_to_user_id)
        # print ("In reply to user ID str:", tweet.in_reply_to_user_id_str)
        # print ("Place:", tweet.place)
        # print ("Retweeted:", tweet.retweeted)
        # print ("Retweet count:", tweet.retweet_count)
        # print ("Source:", tweet.source)
        # print ("Truncated:", tweet.truncated)

#-------------------------------------------------------------------------------
#   B E T A   B R I T E   S T U F F
#-------------------------------------------------------------------------------

class LedDisplayMode:
    ROTATE            = "a"   # Message travels right to left.
    HOLD              = "b"   # Message remains stationary.
    FLASH             = "c"   # Message remains stationary and flashes.
    ROLL_UP           = "e"   # Previous message is pushed up by new message.
    ROLL_DOWN         = "f"   # Previous message is pushed down by new message.
    ROLL_LEFT         = "g"   # Previous message is pushed left by new message.
    ROLL_RIGHT        = "h"   # Previous message is pushed right by new message.
    WIPE_UP           = "i"   # New message is wiped over the previous message from bottom to top.
    WIPE_DOWN         = "j"   # New message is wiped over the previous message from top to bottom.
    WIPE_LEFT         = "k"   # New message is wiped over the previous message from right to left.
    WIPE_RIGHT        = "l"   # New message is wiped over the previous message from left to right.
    SCROLL            = "m"   # New message line pushes the bottom line to the top line if two line unit.
    AUTOMODE          = "o"   # Various modes are called upon to display the message automatically.
    ROLL_IN           = "p"   # Previous message is pushed toward the center of the display by the new message.
    ROLL_OUT          = "q"   # Previous message is pushed outward from the center of the display by the new message.
    WIPE_IN           = "r"   # New message is wiped over the previous message in an inward motion.
    WIPE_OUT          = "s"   # New message is wiped over the previous message in an outward motion.
    COMPRESSED_ROTATE = "t"   # Message travels right to left.  Characters are approximately one half their normal width.  Available only on certain models. (See your Owner's Manual.)
    TWINKLE           = "n0"  # The message will twinkle on the display.
    SPARKLE           = "n1"  # The new message will sparkle on the display over the current message.
    SNOW              = "n2"  # The message will "snow" onto the display.
    INTERLOCK         = "n3"  # The new message will interlock over the current message in alternating rows of dots from each end.
    SWITCH            = "n4"  # Alternating characters "switch" off the display up and down. New message "switches" on in a similar manner.
    SLIDE             = "n5"  # The new message slides onto the display one character at a time from right to left.
    SPRAY             = "n6"  # The new message sprays across and onto the display from right to left.
    STARBURST         = "n7"  # "Starbursts" explode your message onto the display.
    SCRIPT_WELCOME    = "n8"  # The word "Welcome" is written in script across the display.
    SLOT_MACHINE      = "n9"  # Slot machine symbols randomly appear across the display.
    @staticmethod
    def random():
        return 'o'

class LedColor:
    RED         = '\x1c1'
    GREEN       = '\x1c2'
    AMBER       = '\x1c3'
    DIMRED      = '\x1c4'
    DIMGREEN    = '\x1c5'
    BROWN       = '\x1c6'
    ORANGE      = '\x1c7'
    YELLOW      = '\x1c8'
    RAINBOW1    = '\x1c9'
    RAINBOW2    = '\x1cA'
    MIXED       = '\x1cB'
    AUTO        = '\x1cC'
    @staticmethod
    def random():
        return '\x1c'+('%1X' % random.randrange(1,13))

def ledInit():
    global ledSerialPort
    ledSerialPort = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1.0)

def ledSerialSend(rawData):
    global ledSerialPort
    # scrub any remaining unicode or high-ASCII characters
    scrubbedData=''
    for ch in list(rawData):
        try:
            if (ord(ch) <= 127):
                scrubbedData += ch
            else:
                scrubbedData += chr(127)
        except UnicodeDecodeError:
            scrubbedData += '?'
            pass
    ledSerialPort.write(scrubbedData)


def ledDisplay(displayMode,message):
    # 5-20 NULs to clear the line
    ledSerialSend('\000\000\000\000\000\000\000\000\000\000')
    # SOH = "start of heading" = 0x01
    ledSerialSend('\001')
    # Z = broadcast to all displays, 00 address does not matter
    ledSerialSend('Z00')
    # STX = "start of transmission" = 0x02
    ledSerialSend('\002')
    ledSerialSend('AA')
    # vertical alignment, not used on Beta Brite, use ESC space
    ledSerialSend('\033 ')
    # display mode
    ledSerialSend(displayMode)
    ledSerialSend(message)
    # EOT = "end of transmission" = 0x04
    ledSerialSend('\004')

#-------------------------------------------------------------------------------
#   U T I L I T I E S
#-------------------------------------------------------------------------------

EPOCH_DATETIME = datetime.datetime(1970,1,1)
SECONDS_PER_DAY = 24*60*60

def utc_to_local_datetime( utc_datetime ):
    delta = utc_datetime - EPOCH_DATETIME
    utc_epoch = SECONDS_PER_DAY * delta.days + delta.seconds
    time_struct = time.localtime( utc_epoch )
    dt_args = time_struct[:6] + (delta.microseconds,)
    return datetime.datetime( *dt_args )

def sanitizeTweet(before):
    after = before
    # search/replace regexes
    after = re.sub('https?://pic\.twitter\.com/[^ ]*','[IMG]', after)
    after = re.sub('https?://[^ ]*','[LINK]', after)
    after = re.sub('&gt;','>', after)
    after = re.sub('&lt;','<', after)
    after = re.sub('&amp;','&', after)
    after = re.sub('\n',' ', after)
    after = re.sub('\xb0','*', after)       # degree symbol (°)
    after = re.sub('\xe9','e', after)       # accented e (é)
    after = re.sub(u'\u2019',"'", after)    # right single quotation mark (’)
    after = re.sub(u'\u2026','...', after)  # ellipsis (…)
    after = re.sub(u'\u201c','"', after)    # left double quotation mark (“)
    after = re.sub(u'\u201d','"', after)    # right double quotation mark (”)
    return after

def displayFeedback(msgType,detail):
    print(msgType+" >> "+detail)

#-------------------------------------------------------------------------------
#   M A I N   L O O P
#-------------------------------------------------------------------------------

def main():

    global preferences
    ledInit()

    while True:

        # TIME OF DAY

        timeOfDay=datetime.datetime.now().strftime('%m-%d %H:%M:%S')
        displayFeedback('TIME',timeOfDay)
        ledDisplay(LedDisplayMode.HOLD, LedColor.RED+timeOfDay)
        time.sleep(5)

        # GARAGE DOOR

        fname = os.environ['HOME']+'/var/lib/garage.info'
        with open(fname) as f:
            content = f.readlines()
        doorState = '???'
        for line in content:
            line = line.rstrip('\n')
            if (line == 'DOOR=OPEN'):
                doorState = 'open'
            elif (line == 'DOOR=CLOSED'):
                doorState = 'closed'
        displayFeedback('DOOR',doorState)
        ledDisplay(LedDisplayMode.HOLD, LedColor.BROWN+'garage '+doorState)
        time.sleep(5)

        # FLASHBACK
        fname = '/tmp/betabrite.'+str(os.getpid())
        urllib.urlretrieve("http://pogo/status.txt", filename=fname)
        with open(fname) as f:
            content = f.readlines()
        kvpairs = dict(line.rstrip('\n').split('=') for line in content)
        fbStatus = re.sub('_', ' ', kvpairs['status'])
        fbTarget = kvpairs['target']
        fbWait = kvpairs['wait']
        if (fbWait != '0'):
            fbStatus += ' '+fbWait
        displayFeedback('FLASHBACK',fbStatus+' '+fbTarget)
        ledDisplay(LedDisplayMode.ROTATE,
            LedColor.GREEN+'flashback: '+
            LedColor.YELLOW+fbStatus+' '+
            LedColor.ORANGE+fbTarget)
        time.sleep(10)

        # look up Twitter stuff
        try:
            twitterInit()
            twitterUserTimeline = twitterGetUserTweets(preferences.MY_TWEETS)
            twitterHomeTimeline = twitterGetHomeTweets(preferences.OTHER_TWEETS)
        except tweepy.error.TweepError as e:
            print "TWITTER !!! Tweepy error %d: %s" % (e.response.status, e.response.reason)
            twitterUserTimeline = ()
            twitterHomeTimeline = ()
            pass

        # MY TWEETS

        for tweet in reversed(twitterUserTimeline):
            timeStamp = utc_to_local_datetime(tweet.created_at).strftime('%a %H:%M')
            tweetText = sanitizeTweet(tweet.text)
            displayFeedback('MY TWEET', '('+timeStamp+') '+tweetText)
            # RED GREEN AMBER DIMRED DIMGREEN BROWN ORANGE YELLOW RAINBOW1 RAINBOW2 MIXED
            ledDisplay(LedDisplayMode.COMPRESSED_ROTATE,
                LedColor.RED+timeStamp+' '+
                LedColor.YELLOW+tweetText)
            time.sleep(15)

        # INTERMISSION

        displayFeedback('SLOT MACHINE','')
        ledDisplay(LedDisplayMode.SLOT_MACHINE, '')
        time.sleep(5)

        # OTHERS' TWEETS

        for tweet in reversed(twitterHomeTimeline):
            timeStamp = utc_to_local_datetime(tweet.created_at).strftime('%a %H:%M')
            tweetText = sanitizeTweet(tweet.text)
            displayFeedback('PEER TWEET', '('+timeStamp+') '+tweet.user.name+': '+tweetText)
            # RED GREEN AMBER DIMRED DIMGREEN BROWN ORANGE YELLOW RAINBOW1 RAINBOW2 MIXED
            ledDisplay(LedDisplayMode.COMPRESSED_ROTATE,
                LedColor.RED+timeStamp+' '+
                LedColor.ORANGE+tweet.user.name+': '+
                LedColor.GREEN+tweetText)
            time.sleep(15)

    # we never get here
    ledSerialPort.close()

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

