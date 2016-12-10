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

def eventbriteorder():
      response = requests.get(
         "https://www.eventbriteapi.com/v3/users/me/owned_events/?status=live",
         headers = {
             "Authorization": "Bearer JX5ONBLMAVZ7EN2HQTPT",
         },
         verify = True,  # Verify SSL certificate
     )
      data = response.json()
      events = len(data['events'])
      eventid = []
      eventname = []
      for i in range(0, events):
        eventid.append(data['events'][i]['id'])
        eventname.append(data['events'][i]['name']['text'])
      return eventid,eventname

def randombear():
    db = TinyDB('beardb.json')
    bears = db.all()
    randomurl = random.choice(bears)
    return randomurl['url']

def countbears():
    db = TinyDB('beardb.json')
    bears = db.all()
    bearcount = len(bears)
    return bearcount

def merakigetdevices():

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

def cmxgetclients():

   storedCredentials = True
   username = 'learning'
   password = 'learning'
   restURL = 'https://msesandbox.cisco.com:8081/api/location/v2/clients/count'

   if not storedCredentials:
           username = raw_input("Username: ")
           password = raw_input("Password: ")
           storedCredentials = True

           print("----------------------------------")
           print("Authentication string: "+ username+":"+password)
           print("Base64 encoded auth string: " + base64.b64encode(username+":"+password))
           print("----------------------------------")

   try:
           request = requests.get(
           url = restURL,
           auth = HTTPBasicAuth(username,password),
           verify=False)

           parsed = json.loads(request.content)
           clientcount = parsed['count']
           return clientcount
   except requests.exceptions.RequestException as e:
           print(e)

def cmxgetbeacons():

   storedCredentials = True
   username = 'learning'
   password = 'learning'
   restURL = 'https://msesandbox.cisco.com:8081/api/location/v1/beacon/count'

   if not storedCredentials:
           username = raw_input("Username: ")
           password = raw_input("Password: ")
           storedCredentials = True

           print("----------------------------------")
           print("Authentication string: "+ username+":"+password)
           print("Base64 encoded auth string: " + base64.b64encode(username+":"+password))
           print("----------------------------------")

   try:
           request = requests.get(
           url = restURL,
           auth = HTTPBasicAuth(username,password),
           verify=False)

           parsed = json.loads(request.content)
           beaconcount = parsed
           return beaconcount
   except requests.exceptions.RequestException as e:
           print(e)


def cmxgetclientmac():

   storedCredentials = True
   username = 'learning'
   password = 'learning'
   restURL = 'https://msesandbox.cisco.com:8081/api/location/v2/clients'
   clientmac = []
   if not storedCredentials:
           username = raw_input("Username: ")
           password = raw_input("Password: ")
           storedCredentials = True

           print("----------------------------------")
           print("Authentication string: "+ username+":"+password)
           print("Base64 encoded auth string: " + base64.b64encode(username+":"+password))
           print("----------------------------------")

   try:
           request = requests.get(
           url = restURL,
           auth = HTTPBasicAuth(username,password),
           verify=False)

           parsed = json.loads(request.content)
           clientcount = len(parsed)
           for x in range(0, clientcount):
               clientmac.append(parsed[x]["macAddress"])
           return clientmac
   except requests.exceptions.RequestException as e:
           print(e)

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
        elif 'trainingdayreg' in in_message:
            eventid,eventname = eventbriteorder()
            msg += "<h1>Training Day Registrations</h1>"
            for i in range(0, len(eventid)):
                    response = requests.get(
                    "https://www.eventbriteapi.com/v3/events/%s/orders" % (eventid[i], ),
                    headers = {
                    "Authorization": "Bearer JX5ONBLMAVZ7EN2HQTPT",
                    },
                    verify = True,
                    )
                    data = response.json()
                    numorders = len(data['orders'])
                    msg += "<h2>"
                    msg += eventname[i]
                    msg += "</h2>"
                    msg += u'\n\n'
                    for i in range(0, numorders):
                        msg += 'Name:'
                        msg += data['orders'][i]['name']
                        msg += u'\n'
                        msg += data['orders'][i]['email']
                        msg += u'\n\n'
        elif 'what do we do?' in in_message:
            msg = "<h1>We Hunt We Fight We WIN!<h1>"
        elif 'jimmyjams' in in_message:
            msg = "Im all about the Jimmy Jams!"
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
            msg = "I only do pre sales you should call Cisco TAC at 1 800 553 2447"
        elif 'howmanybears' in in_message:
            bearcount = countbears()
            msg = bearcount
        elif 'randombear' in in_message:
            randomurl = randombear()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": randomurl})
        elif 'dancingbears' in in_message:
            print "Databears get Funky!"
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": bat_signal})
        elif 'hulabears' in in_message:
            print "Databears get Funky!"
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": hula_bears})
        elif 'sharonbday' in in_message:
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": happy_bday})
        elif 'snorlax' in in_message:
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": snorlax})
        elif 'sparkboard' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": sparkboard})
             msg = "You really need to collaborate on Spark Board, this is what you get with Surface Hub or Google Jamboard"
        elif 'laserfocus' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": laserfocus})
        elif 'manatee' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": manatee})
        elif 'raiders' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": raiders})
         elif 'chucknorris' in in_message:
             randomquote = chucknorris()
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": randomquote})
        elif 'touchdown' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": touchdown})
        elif 'osupokes' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": osu1})
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": osu2})
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": touchdown})
        elif 'micdrop' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": micdrop})
        elif 'agile' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": agile})
        elif 'ghettoblaster' in in_message:
             sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": ghettoblaster})
        if msg != None:
            print msg
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
    return "true"



####CHANGE THESE VALUES#####
bot_email = "fightclub@sparkbot.io"
bot_name = "fightclub"
bearer = "MzRkMTE3ODctMTMwZC00YmQ5LTliNjMtZDZhNGE0MjE1N2U4ODg2MDNmOTctNWFm"
bat_signal  = "http://www.gifbin.com/bin/163563561.gif"
happy_bday = "http://bestanimations.com/Holidays/Birthday/funnybithdaygifs/funny-star-wars-darth-vaderdancing--happy-birthday-gif.gif"
hula_bears = "http://i.imgur.com/Bz2n7KR.gif"
snorlax = "https://media.giphy.com/media/11g5IteO9JjpgA/giphy.gif"
sparkboard = "https://media.giphy.com/media/14wPFMQBn66xwI/giphy.gif"
laserfocus = "https://media.giphy.com/media/ruCg20L6H72TK/giphy.gif"
manatee = "https://media.giphy.com/media/6kbx5578gUAJa/giphy.gif"
raiders = "https://media.giphy.com/media/3ofT5yXYtGFv7G3I5O/giphy.gif"
touchdown = "https://media.giphy.com/media/1434lafyjzMk1y/source.gif"
osu1 = "https://media.giphy.com/media/291XZD4vUtiuY/giphy.gif"
osu2 = "https://media.giphy.com/media/14skUVRkuqgekg/source.gif"
micdrop = "https://media.giphy.com/media/Yt3aZ6wj8AXJK/giphy.gif"
agile = "https://media.giphy.com/media/n3FEnZX92MekM/giphy.gif"
ghettoblaster = "https://media.giphy.com/media/WI17euXijqDqU/giphy.gif"
run_itty(server='wsgiref', host='0.0.0.0', port=10010)
