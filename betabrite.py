#!/usr/bin/env python
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
import traceback
import unicodedata
import signal

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
    preferences.twitter_user = config.get('preferences', 'twitter.user')
    preferences.twitter_mine_count = int(config.get('preferences', 'twitter.mine.count'))
    preferences.twitter_mine_delay = float(config.get('preferences', 'twitter.mine.delay'))
    preferences.twitter_peer_count = int(config.get('preferences', 'twitter.peer.count'))
    preferences.twitter_peer_delay = float(config.get('preferences', 'twitter.peer.delay'))

    twitterAuth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    twitterAuth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    twitterApi = tweepy.API(twitterAuth, secure=True)

def twitterGetUserTweets(i):
    global twitterApi
    global preferences
    twitterUserObj = twitterApi.get_user(preferences.twitter_user)
    return twitterApi.user_timeline(screen_name=preferences.twitter_user, include_rts=True, count=i)

def twitterGetHomeTweets(i):
    global twitterApi
    global preferences
    twitterUserObj = twitterApi.get_user(preferences.twitter_user)
    return  twitterApi.home_timeline(screen_name=preferences.twitter_user, include_rts=True, count=i)

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
        except:
            raise
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

def unicodeHtmlToAscii(original):
    # Get the input into Unicode format.
    unicodeStr = u'';
    if isinstance(original, unicode):
        unicodeStr = original
    if isinstance(original, str):
        unicodeStr = unicode(original, 'utf-8')
    # Replace links with a place-holder.
    unicodeStr = re.sub(u'https?://pic\.twitter\.com/[^ ]*', u'[IMG]', unicodeStr)
    unicodeStr = re.sub(u'https?://[^ ]*', u'[LINK]', unicodeStr)
    # Replace HTML markup with simple ASCII equivalents.
    unicodeStr = re.sub(u'&gt;', u'>', unicodeStr)
    unicodeStr = re.sub(u'&lt;', u'<', unicodeStr)
    unicodeStr = re.sub(u'&amp;', u'&', unicodeStr)
    unicodeStr = re.sub(u'\n', u' ', unicodeStr)
    # Replace specific unicode characters with ASCII equivalents.
    unicodeStr = re.sub(u'\xb0', u'*', unicodeStr)       # degree symbol (°)
    unicodeStr = re.sub(u'\xe9', u'e', unicodeStr)       # accented e (é)
    unicodeStr = re.sub(u'\u2014', u"-", unicodeStr)    # em-dash (—)
    unicodeStr = re.sub(u'\u2018', u"'", unicodeStr)    # left single quotation mark (‘)
    unicodeStr = re.sub(u'\u2019', u"'", unicodeStr)    # right single quotation mark (’)
    unicodeStr = re.sub(u'\u2026', u'...', unicodeStr)  # ellipsis (…)
    unicodeStr = re.sub(u'\u201c', u'"', unicodeStr)    # left double quotation mark (“)
    unicodeStr = re.sub(u'\u201d', u'"', unicodeStr)    # right double quotation mark (”)
    unicodeStr = re.sub(u'\u262e', u'@', unicodeStr)    # peace (☮)
    # Finally, try to convert all unicode to their base ASCII characters, ignore what you can't convert.
    # http://stackoverflow.com/questions/2365411/python-convert-unicode-to-ascii-without-errors
    unicodeStr = unicodedata.normalize('NFKD', unicodeStr)   # see http://unicode.org/reports/tr15/
    asciiStr = unicodeStr.encode('ascii', 'ignore')
#   if asciiStr != unicodeStr:
#       print("unicode conversion > "+asciiStr)
    return asciiStr

def displayFeedback(msgType,detail):
    logTime=datetime.datetime.now().strftime('%H:%M:%S')
    print(logTime+' '+msgType+" >> "+detail)

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

        content = ''
        try:
            fname = '/tmp/betabrite.'+str(os.getpid())
            urllib.urlretrieve("http://garagepi/", filename=fname)
            with open(fname) as f:
                content = f.readlines()
        except IOError:
            pass

        doorState = '???'
        if len(content) > 0:
            for line in content:
                line = line.rstrip('\n')
                if (line == 'DOOR=OPEN'):
                    doorState = 'open'
                elif (line == 'DOOR=CLOSED'):
                    doorState = 'closed'

        displayFeedback('DOOR','garage '+doorState)
        ledDisplay(LedDisplayMode.HOLD, LedColor.BROWN+'garage '+doorState)
        time.sleep(5)

        # FLASHBACK

        fname = '/tmp/betabrite.'+str(os.getpid())
        content = ''
        try:
            urllib.urlretrieve("http://pogo/status.txt", filename=fname)
            with open(fname) as f:
                content = f.readlines()
        except IOError:
            pass

        fbTarget = '???'
        fbStatus = ''
        if len(content) > 0:
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

        # INTERMISSION

        displayFeedback('SLOT MACHINE','5s')
        ledDisplay(LedDisplayMode.SLOT_MACHINE, '')
        time.sleep(5)

        # LOOK UP TWITTER STUFF

        try:
            twitterInit()
            twitterUserTimeline = twitterGetUserTweets(preferences.twitter_mine_count)
            twitterHomeTimeline = twitterGetHomeTweets(preferences.twitter_peer_count)
        except tweepy.error.TweepError as e:
            # we did not get anything from Twitter, so don't show any messages
            twitterUserTimeline = ()
            twitterHomeTimeline = ()
            # show some info about the error
            response = e.response
            status = 0
            if response == None:
                print "TWITTER !!! unknown Tweepy error"
            else:
                print "TWITTER !!! Tweepy error %d: %s" % (e.response.status, e.response.reason)
                if e.response.status == 429:
                    displayFeedback('PAUSE FOR TWITTER API RESET','60s')
                    ledDisplay(LedDisplayMode.SNOW, 'TWITTER ERROR')
                    time.sleep(60)
            pass

        # MY TWEETS

        for tweet in reversed(twitterUserTimeline):
            timeStamp = utc_to_local_datetime(tweet.created_at).strftime('%a %H:%M')
            tweetText = unicodeHtmlToAscii(tweet.text)
            displayFeedback('MY TWEET', '('+timeStamp+') '+tweetText)
            # RED GREEN AMBER DIMRED DIMGREEN BROWN ORANGE YELLOW RAINBOW1 RAINBOW2 MIXED
            ledDisplay(LedDisplayMode.COMPRESSED_ROTATE,
                LedColor.RED+timeStamp+' '+
                LedColor.YELLOW+tweetText)
            time.sleep(preferences.twitter_mine_delay)

        # INTERMISSION

        if len(twitterUserTimeline) > 0:
            displayFeedback('SLOT MACHINE','5s')
            ledDisplay(LedDisplayMode.SLOT_MACHINE, '')
            time.sleep(5)

        # OTHERS' TWEETS

        for tweet in reversed(twitterHomeTimeline):
            timeStamp = utc_to_local_datetime(tweet.created_at).strftime('%a %H:%M')
            tweetUser = unicodeHtmlToAscii(tweet.user.name)
            tweetText = unicodeHtmlToAscii(tweet.text)
            displayFeedback('PEER TWEET', '('+timeStamp+') '+tweetUser+': '+tweetText)
            # RED GREEN AMBER DIMRED DIMGREEN BROWN ORANGE YELLOW RAINBOW1 RAINBOW2 MIXED
            ledDisplay(LedDisplayMode.COMPRESSED_ROTATE,
                LedColor.RED+timeStamp+' '+
                LedColor.ORANGE+tweet.user.name+': '+
                LedColor.GREEN+tweetText)
            time.sleep(preferences.twitter_peer_delay)

        # INTERMISSION

        if len(twitterHomeTimeline) > 0:
            displayFeedback('SLOT MACHINE','5s')
            ledDisplay(LedDisplayMode.SLOT_MACHINE, '')
            time.sleep(5)

    # we never get here
    ledSerialPort.close()

#-------------------------------------------------------------------------------

def signal_handler(signal, frame):
    print('received HUP signal')
    ledDisplay(LedDisplayMode.HOLD, '')
    sys.exit(0)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    signal.signal(signal.SIGHUP, signal_handler)
    while True:
        try:
            main()
        except SystemExit:
            print('exiting')
            raise
        except:
            print("CRASH: "+str(sys.exc_info()[0]))
            tb = traceback.format_exc()
            print(tb)
            time.sleep(5)

