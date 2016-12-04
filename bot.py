#! /usr/bin/python
from itty import *
import urllib2
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
import string
from Datatypes import *

# Create the Flask application that provides the bot foundation
app = Flask(__name__)


# The list of commands the bot listens for
# Each key in the dictionary is a command
# The value is the help message sent for the command
commands = {
    "/rules": "You're not allowed to talk about it.",
    "/tylerdurden": "famous Tyler quotes.",
    "/chucknorris": "You don't ask Chuck Norris questions."
}


# Not strictly needed for most bots, but this allows for requests to be sent
# to the bot from other web sites.  "CORS" Requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,Key')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


# Entry point for Spark Webhooks
@app.route('/', methods=["POST"])
def process_webhook():
    # Check if the Spark connection has been made
    if spark is None:
        sys.stderr.write("Bot not ready.  \n")
        return "Spark Bot not ready.  "

    post_data = request.get_json(force=True)
    # Uncomment to debug
    # sys.stderr.write("Webhook content:" + "\n")
    # sys.stderr.write(str(post_data) + "\n")

    # Take the posted data and send to the processing function
    process_incoming_message(post_data)
    return ""


# Config Endpoint to set Spark Details
@app.route('/config', methods=["GET", "POST"])
def config_bot():
    if request.method == "POST":
        post_data = request.get_json(force=True)
        # Verify that a token and email were both provided
        if "SPARK_BOT_TOKEN" not in post_data.keys() or "SPARK_BOT_EMAIL" not in post_data.keys():
            return "Error: POST Requires both 'SPARK_BOT_TOKEN' and 'SPARK_BOT_EMAIL' to be provided."

        # Setup Spark
        spark_setup(post_data["SPARK_BOT_EMAIL"], post_data["SPARK_BOT_TOKEN"])

    # Return the config detail to API requests
    config_data = {
        "SPARK_BOT_EMAIL": bot_email,
        "SPARK_BOT_TOKEN": spark_token,
        "SPARK_BOT_URL": bot_url,
        "SPARKBOT_APP_NAME": bot_app_name
    }
    config_data["SPARK_BOT_TOKEN"] = "REDACTED"     # Used to hide the token from requests.
    return json.dumps(config_data)


# Quick REST API to have bot send a message to a user
@app.route("/hello/<email>", methods=["GET"])
def message_email(email):
    """
    Kickoff a 1 on 1 chat with a given email
    :param email:
    :return:
    """
    # Check if the Spark connection has been made
    if spark is None:
        sys.stderr.write("Bot not ready.  \n")
        return "Spark Bot not ready.  "

    # send_message_to_email(email, "Hello!")
    spark.messages.create(toPersonEmail=email, markdown="Hello!")
    return "Message sent to " + email


# Health Check
@app.route("/health", methods=["GET"])
def health_check():
    """
    Notify if bot is up
    :return:
    """
    return "Up and healthy"


# Function to Setup the WebHook for the bot
def setup_webhook(name, targeturl):
    # Get a list of current webhooks
    webhooks = spark.webhooks.list()

    # Look for a Webhook for this bot_name
    # Need try block because if there are NO webhooks it throws an error
    try:
        for h in webhooks:  # Efficiently iterates through returned objects
            if h.name == name:
                sys.stderr.write("Found existing webhook.  Updating it.\n")
                wh = spark.webhooks.update(webhookId=h.id, name=name, targetUrl=targeturl)
                # Stop searching
                break
        # If there wasn't a Webhook found
        if wh is None:
            sys.stderr.write("Creating new webhook.\n")
            wh = spark.webhooks.create(name=name, targetUrl=targeturl, resource="messages", event="created")
    except:
        sys.stderr.write("Creating new webhook.\n")
        wh = spark.webhooks.create(name=name, targetUrl=targeturl, resource="messages", event="created")

    return wh


# Function to take action on incoming message
def process_incoming_message(post_data):
    # Determine the Spark Room to send reply to
    room_id = post_data["data"]["roomId"]

    # Get the details about the message that was sent.
    message_id = post_data["data"]["id"]
    message = spark.messages.get(message_id)
    # Uncomment to debug
    # sys.stderr.write("Message content:" + "\n")
    # sys.stderr.write(str(message) + "\n")

    # First make sure not processing a message from the bot
    if message.personEmail in spark.people.me().emails:
        # Uncomment to debug
        # sys.stderr.write("Message from bot recieved." + "\n")
        return ""

    # Log details on message
    sys.stderr.write("Message from: " + message.personEmail + "\n")

    # Find the command that was sent, if any
    command = ""
    for c in commands.items():
        if message.text.find(c[0]) != -1:
            command = c[0]
            sys.stderr.write("Found command: " + command + "\n")
            # If a command was found, stop looking for others
            break

    reply = ""
    # Take action based on command
    # If no command found, send help
    if command in ["", "/rules"]:
        reply = rule(post_data)
    elif command in ["/echo"]:
        reply = send_echo(message)
    elif command in ["/chucknorris"]:
        reply = chuck_joke()

    # send_message_to_room(room_id, reply)
    spark.messages.create(roomId=room_id, markdown=reply)


# Sample command function that just echos back the sent message
def send_echo(incoming):
    # Get sent message
    message = extract_message("/echo", incoming.text)
    return message


# Construct a help message for users.
def rule():
    fr = TinyDB('frules.json')
    rules = fr.all()
    randomquote = random.choice(rules)
    return randomquote['quote']
def rule(post_data):
    response = "Hello!  "
    message = message + "I understand the following commands:  \n"
    for c in commands.items():
        message = message + "* **%s**: %s \n" % (c[0], c[1])
    return message

# Chuck Norrise Joke
def chuck_joke():
    #use urllib2 to get random joke
    import urllib2

    response = urllib2.urlopen('http://api.icndb.com/jokes/random')
    joke = json.loads(response.read())["value"]["joke"]
    # return the text of the joke
    return joke

# Return contents following a given command
def extract_message(command, text):
    cmd_loc = text.find(command)
    message = text[cmd_loc + len(command):]
    return message


# Setup the Spark connection and WebHook
def spark_setup(email, token):
    # Update the global variables for config details
    globals()["spark_token"] = token
    globals()["bot_email"] = email

    sys.stderr.write("Spark Bot Email: " + bot_email + "\n")
    sys.stderr.write("Spark Token: REDACTED\n")

    # Setup the Spark Connection
    globals()["spark"] = CiscoSparkAPI(access_token=globals()["spark_token"])
    globals()["webhook"] = setup_webhook(globals()["bot_app_name"], globals()["bot_url"])
    sys.stderr.write("Configuring Webhook. \n")
    sys.stderr.write("Webhook ID: " + globals()["webhook"].id + "\n")


if __name__ == '__main__':
    # Entry point for bot
    # Retrieve needed details from environment for the bot
    #bot_email = os.getenv("SPARK_BOT_EMAIL")
    #spark_token = os.getenv("SPARK_BOT_TOKEN")
    #bot_url = os.getenv("SPARK_BOT_URL")
    #bot_app_name = os.getenv("SPARK_BOT_APP_NAME")
    bot_email = "fightclub@sparkbot.io"
    spark_token = "M2Y4MTBlNmYtYTBhNS00NTU0LWE2M2MtNmY2N2IxNDExNGMwZmFiZjkyMTItMjk4"
    bot_url = "http://sytomas-fightclub.app.mantldevnetsandbox.com"
    bot_app_name = "fightclub"

    # bot_url and bot_app_name must come in from Environment Variables
    if bot_url is None or bot_app_name is None:
            sys.exit("Missing required argument.  Must set 'bot_url' and 'bot_app_name'.")

    # Write the details out to the console
    sys.stderr.write("Spark Bot URL (for webhook): " + bot_url + "\n")
    sys.stderr.write("Spark Bot App Name: " + bot_app_name + "\n")

    # Placeholder variables for spark connection objects
    spark = None
    webhook = None

    # Check if the token and email were set in ENV
    if spark_token is None or bot_email is None:
        sys.stderr.write("Spark Config is missing, please provide via API.  Bot not ready.\n")
    else:
        spark_setup(bot_email, spark_token)
        spark = CiscoSparkAPI(access_token=spark_token)

    #app.run(debug=True, host='0.0.0.0', port=int("5000"))


#Entered by Syd Tomas

@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    further actions are taken.
    """
    webhook = json.loads(request.body)
    print webhook['data']['id']
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    msg = ''
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        if 'rules' in in_message:
            randomquote = rule()
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": randomquote})
        elif 'tylerdurden' in in_message:
            print "Sticking feathers up your butt does not make you a chicken.!"
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": fightclub})
        elif 'hulabears' in in_message:
            print "Databears get Funky!"
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": hula_bears})
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
fightclub  = "http://giphy.com/search/fight-club"
happy_bday = "http://bestanimations.com/Holidays/Birthday/funnybithdaygifs/funny-star-wars-darth-vaderdancing--happy-birthday-gif.gif"
hula_bears = "http://i.imgur.com/Bz2n7KR.gif"
#run_itty(server='wsgiref', host='0.0.0.0', port=10010)
