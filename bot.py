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
    the fightgif definition retrieves a random gif link from the 'fggif.json'
    """
    fg = TinyDB('fggif.json')
    fggif = fg.all()
    randomgif = random.choice(fggif)
    return randomgif['gif']

def getmerakidevices():

    url = 'https://n131.meraki.com/api/v0/networks/L_636696397319504780/devices'
    headers = {'X-Cisco-Meraki-API-Key': '158adab9d93235d072e3258a3644d3af3b346e21'}
    devicemodel = []
    deviceserial = []
    r = requests.get(url, headers=headers)

    binary = r.content
    output = json.loads(binary)

    numdevices = len(output)
    for x in range(0, numdevices):
        devicemodel.append(output[x]["model"])
        deviceserial.append(output[x]["serial"])
    return devicemodel,deviceserial

#******************************************************
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
#******************************************************


@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    further actions are taken. i.e.
    """
    webhook = json.loads(request.body)
    print webhook['data']['id']
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    print result
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        if '/rules' in in_message:
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": fcruleimg})
            msg = "1st RULE: You do not talk about FIGHT CLUB.\n"
            msg += "2nd RULE: You DO NOT talk about FIGHT CLUB.\n"
            msg += '3rd RULE: If someone says "stop" or goes limp, taps out the fight is over.\n'
            msg += "4th RULE: Only two guys to a fight.\n"
            msg += "5th RULE: One fight at a time.\n"
            msg += "6th RULE: No shirts, no shoes.\n"
            msg += "7th RULE: Fights will go on as long as they have to.\n"
            msg += "8th and final RULE: If this is your first night at FIGHT CLUB, you HAVE to fight."
        elif '/batcave' in in_message:
            message = result.get('text').split('batcave')[1].strip(" ")
            if len(message) > 0:
                msg = "The Batcave echoes, '{0}'".format(message)
            else:
                msg = "The Batcave is silent..."
        elif '/help'in in_message:
            msg = "Commands I understand: \n"
            msg += "/rules - Rules of Fight Club. \n"
            msg += "/fightgif - sends random Fight Club movie gifs. \n"
            msg += "/chucknorris - Chuck Norris needs no explanation. \n"
        elif '/fightgif' in in_message:
            fight = fightgif()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": fight})
        elif '/chucknorris' in in_message:
            joke = chucknorris()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": joke})
        elif '/merakidevices' in in_message:
            devicemodel,deviceserial = getmerakidevices()
            for i in range(0, len(devicemodel)):
                msg = 'Model:'
                msg += devicemodel[i]
                msg += u'\t'
                msg += 'Serial:'
                msg += deviceserial[i]
                msg += u'\n'
        if msg != None:
            print msg
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
    return "true"


####CHANGE THESE VALUES#####
bot_email = "fightclub@sparkbot.io"
bot_name = "fightclub"
bearer = "MzJjZDAxNWUtOTIzZC00MTdmLTg0MWQtMjVkY2ZkNjU0ZmYxZDdjZDM1NjgtYWMw" #fightclub bearer token
#bearer = "YmZiZTg0N2ItZTZhOS00YTM4LTkyZTYtNzJlZTA2MDZhOGY3MTQ4NTEzNjEtMDA2" #My Bearer Token
#bearer = "M2ZjMjcxODQtMmFlYi00YWJiLWExYWYtMDBkYThmZDU2N2UyNzk5NTc2NjctNDgx" #updated
fcruleimg = "http://www.diggingforfire.net/sitegfx/FightClub.jpg"
bat_signal  = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"
run_itty(server='wsgiref', host='0.0.0.0', port=10010)
