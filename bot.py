#!/usr/bin/python

from itty import *
import urllib2
import json
import requests
#requests.packages.urllib3.disable_warnings()
from requests.auth import HTTPBasicAuth
import base64
import random
from tinydb import TinyDB, Query
from flask import Flask, request
from ciscosparkapi import CiscoSparkAPI
import os
import sys
import json
import re

def chucknorris():
    """
    chucknorris - no explanation needed.'
    """
    response = urllib2.urlopen('http://api.icndb.com/jokes/random')
    joke = json.loads(response.read())["value"]["joke"]
    return joke

def rules():
    fc = TinyDB('frules.json')
    rule = fc.all()
    randomurl = random.choice(rule)
    return randomurl['quote']

def fightgif():
    """
    the fightgif definition retrieves random a gif link from the 'fggif.json'
    """
    fg = TinyDB('fggif.json')
    fggif = fg.all()
    randomgif = random.choice(fggif)
    return randomgif['gif']

def sendSparkGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    further actions are taken. i.e.
    /batman    - replies to the room with text
    /batcave   - echoes the incoming text to the room
    /batsignal - replies to the room with an image
    """
    webhook = json.loads(request.body)
    print webhook['data']['id']
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        if 'rules' in in_message:
            #fcrules = rules()
            #sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": fcrules})
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": fcruleimg})
            msg = "1st RULE: You do not talk about FIGHT CLUB. \n"
            msg += "2nd RULE: You DO NOT talk about FIGHT CLUB."
            msg += "2nd RULE: You DO NOT talk about FIGHT CLUB."
            msg += '3rd RULE: If someone says "stop" or goes limp, taps out the fight is over.'
            msg += "4th RULE: Only two guys to a fight."
            msg += "5th RULE: One fight at a time."
            msg += "6th RULE: No shirts, no shoes."
            msg += "7th RULE: Fights will go on as long as they have to." 
            msg += "8th and final RULE: If this is your first night at FIGHT CLUB, you HAVE to fight."
        elif 'batcave' in in_message:
            message = result.get('text').split('batcave')[1].strip(" ")
            if len(message) > 0:
                msg = "The Batcave echoes, '{0}'".format(message)
            else:
                msg = "The Batcave is silent..."
        elif 'fightgif' in in_message:
            fight = fightgif()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": fight})
        elif 'chucknorris' in in_message:
            joke = chucknorris()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": joke})
        if msg != None:
            print msg
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
    return "true"


####CHANGE THESE VALUES#####
bot_email = "fightclub@sparkbot.io"
bot_name = "fightclub"
fcruleimg = "http://www.diggingforfire.net/sitegfx/FightClub.jpg"
bearer = "YmZiZTg0N2ItZTZhOS00YTM4LTkyZTYtNzJlZTA2MDZhOGY3MTQ4NTEzNjEtMDA2"
bat_signal  = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"
run_itty(server='wsgiref', host='0.0.0.0', port=10010)
