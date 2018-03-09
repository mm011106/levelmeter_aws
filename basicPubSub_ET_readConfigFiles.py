#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from datetime import *
import logging
import time
import argparse
import json
import commands

AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: %s" % message.payload)
    print("from topic: %s" % message.topic)
    print("--------------\n\n")


# Read in command-line parameters
# parser = argparse.ArgumentParser()
# parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
# parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
# parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
# parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
# parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
#                     help="Use MQTT over WebSocket")
# parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
#                     help="Targeted client id")
# parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
# parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
#                     help="Operation modes: %s"%str(AllowedActions))
# parser.add_argument("-M", "--message", action="store", dest="message", default="Hello from Eagle Tech.",
#                     help="Message to publish")

# args = parser.parse_args()
with open('connectConf.json','r') as f:
    connectConf = json.load(f)

with open('topicConf.json','r') as f:
    topicConf = json.load(f)
    
host = connectConf["endpoint"]
rootCAPath = connectConf["rootCAPath"]
certificatePath = connectConf["certificatePath"]
privateKeyPath = connectConf["privateKeyPath"]
useWebsocket =  connectConf["useWebsocket"]
clientId = connectConf["siteID"]

topic = topicConf["topic"]


if topicConf["mode"] not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (topicConf["mode"], str(AllowedActions)))
    exit(2)

if connectConf["useWebsocket"] and connectConf["certificatePath"] and connectConf["privateKeyPath"]:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not connectConf["useWebsocket"] and (not connectConf["certificatePath"] or not connectConf["privateKeyPath"]):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.ERROR)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, 443)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
if topicConf["mode"] == 'both' or topicConf["mode"] == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

# Publish to the same topic in a loop forever
# loopCount = 0
while True:
    if topicConf["mode"] == 'both' or topicConf["mode"] == 'publish':
        message = {}
        message['timestamp']=str(int( time.mktime( datetime.now().timetuple() ) ))
        message['IP']=commands.getoutput('hostname -I')
#         message['message'] = args.message
#         message['sequence'] = loopCount
        messageJson = json.dumps(message)
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        if topicConf["mode"] == 'publish':
            print('Published topic %s: %s\n' % (topic, messageJson))
#         loopCount += 1
    time.sleep(10)