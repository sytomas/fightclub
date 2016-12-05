#!/usr/bin/python

from itty import *
import urllib2
import json
import requests
requests.packages.urllib3.disable_warnings()
from requests.auth import HTTPBasicAuth
import base64
import random
from tinydb import TinyDB, Query
from flask import Flask, request
from ciscosparkapi import CiscoSparkAPI
import os
import sys
import json

commands = {
    "/help": "Get help.",
    "/chuck": "Get a random Chuck Norris Joke."
}

def rules():
    fc = TinyDB('frules.json')
    rule = db.all()
    randomrule = random.choice(rule)
    return randomrule['quote']

def chucknorris():
    response = urllib2.urlopen('http://api.icndb.com/jokes/random')
    joke = json.loads(response.read())["value"]["joke"]
    return joke

def lmgtfy():
    msg = "Let me get that for you:"
    return urllib2.urlopen('https://lmgtfy.com/?q=') + word

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
        if 'databears' in in_message or "favorite" in in_message:
            msg = "I Love Databears!"
        elif 'trainingdaystatus' in in_message:
            eventid,eventname = eventbriteorder()
            for i in range(0, len(eventid)):
                for x in eventname:
                    response = requests.get(
                    "https://www.eventbriteapi.com/v3/reports/attendees/?event_ids=%s" % (eventid[i], ),
                    headers = {
                    "Authorization": "Bearer JX5ONBLMAVZ7EN2HQTPT",
                    },
                    verify = True,
                    )
                data = response.json()
                msg += 'Event Name:'
                msg += eventname[i]
                msg += u'\n'
                msg += 'Event ID:'
                msg += eventid[i]
                msg += u'\n'
                msg += 'Total Attendees:'
                msg += str(data['totals']['num_attendees'])
                msg += u'\n'
                msg += 'Total Orders:'
                msg += str(data['totals']['num_orders'])
                msg += u'\n'
                msg += u'\n'
        elif 'merakidevices' in in_message:
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
            word = raw_input('what do you need help with? ')
            randomurl = lmgtfy()
        elif 'howmanybears' in in_message:
            bearcount = countbears()
            msg = bearcount
        elif 'fightclub' in in_message:
            randomquote = fightclub()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": randomurl})
        elif 'chucknorris' in in_message:
            randomquote = chucknorris()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": randomurl})
        elif 'sharonbday' in in_message:
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": happy_bday})
        if msg != None:
            print msg
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
    return "true"



####CHANGE THESE VALUES#####
bot_email = "fightclub@sparkbot.io"
bot_name = "fightclub"
bearer = "M2Y4MTBlNmYtYTBhNS00NTU0LWE2M2MtNmY2N2IxNDExNGMwZmFiZjkyMTItMjk4"
fightclub = "http://giphy.com/search/fight-club"
happy_bday = "http://giphy.com/search/happy-birthday"
run_itty(server='wsgiref', host='0.0.0.0', port=10010)
