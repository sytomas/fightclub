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

commands = {
    "/help": "Get help.",
    "/rules": "Rules of Fight Club"
    "/gif": "Random GIFs from Fight Club"
    "/chucknorris": "You don't ask about Chuck Norris"
}

def rules():
    fc = TinyDB('frules.json')
    rule = fc.all()
    randomurl = random.choice(rule)
    return randomurl['quote']

def chucknorris():
    response = urllib2.urlopen('http://api.icndb.com/jokes/random')
    joke = json.loads(response.read())["value"]["joke"]
    return joke

def lmgtfy():
    msg = "Let me get that for you:"
    text = re.sub(r'( )', r'\1+', word)
    smerge = "".join(text.split()) # removes spaces
    baseurl = "https://lmgtfy.com/?q="
    finalurl = baseurl + smerge
    webbrowser.open(finalurl)

def fightgif():
    fg = TinyDB('fgif.json')
#    fg = urllib2.urlopen('http://giphy.com/search/fight-club')
    fggif = fg.all
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
    msg = ''
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        if 'merakidevices' in in_message:
            devicemodel,deviceserial = merakigetdevices()
            for i in range(0, len(devicemodel)):
                msg += 'Model:'
                msg += devicemodel[i]
                msg += u'\t'
                msg += 'Serial:'
                msg += deviceserial[i]
                msg += u'\n'
        elif 'cmxactiveclients' in in_message:
            clientcount = cmxgetclients()
            msg = "Active Clients for DevNetCampus>DevNetBuilding>DevNetZone>Zone1: %s" % clientcount
        elif 'cmxactivebeacons' in in_message:
            beaconcount = cmxgetbeacons()
            msg = "Active Beacons for DevNetCampus>DevNetBuilding>DevNetZone>Zone1: %s" % beaconcount
        elif 'cmxclientmac' in in_message:
            clientmac = cmxgetclientmac()
            for i in clientmac:
                msg += i
                msg += u'\n'
        elif 'help' in in_message:
            #word = raw_input('what do you need help with? ')
            msg = "What do you need help with?"
            #text = re.sub(r'( )', r'\1+', word)
            #smerge = "".join(text.split()) # removes spaces
            randomurl = lmgtfy()
        elif 'rules' in in_message:
            randomurl = rules()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": randomurl})
        elif 'fight' in in_message:
#            randomurl =
            randomquote = fightclub()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": randomurl})
        elif 'chucknorris' in in_message:
            randomquote = chucknorris()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": randomurl})
        if msg != None:
            print msg
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
    return "true"



####CHANGE THESE VALUES#####
bot_email = "fightclub@sparkbot.io"
bot_name = "fightclub"
bearer = "M2Y4MTBlNmYtYTBhNS00NTU0LWE2M2MtNmY2N2IxNDExNGMwZmFiZjkyMTItMjk4"
run_itty(server='wsgiref', host='0.0.0.0', port=10010)
