##########################################################
#
# Simple app to test parsing of json responses
# from Twitter API v2 in order to avoid spending
# number of requests (in the basic model it has a monthly
# limit).
#
#
# json responses from API have been saved in .txt files
# jsonResponse-ExampleX.txt (where X a number) etc
#
# @25/12/2021
##########################################################




#For sending GET requests from the API
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API
import json
# For displaying the data after
import pandas as pd
# For saving the response data in CSV format
import csv
# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
import unicodedata
#To add wait time between requests
import time

# Read json file
f = open("jsonResponse-Example-1.txt", "r")
jsonData = json.load(f)
f.close()

#
# TODO: jsonData['includes']['users'] to get userdata
#

numProcessed = 0
numRetweets = 0

userObs = {}

totalUsers = len(jsonData['includes']['users'])
for k in range(totalUsers):
    userObs[jsonData['includes']['users'][k]['id']] = jsonData['includes']['users'][k]
    #userIds.append(jsonData['includes']['users'][k]['id'])


totalTweets = len(jsonData['data'])
for i in range( totalTweets ):
    numProcessed += 1
    if 'referenced_tweets' in jsonData['data'][i]:
        if jsonData['data'][i]['referenced_tweets'][0]['type'] == 'retweeted':
           numRetweets += 1
        else:
             tweetUrl =  "https://twitter.com/i/web/status/" + jsonData['data'][i]['id']
             # NOTE: number shown before ) is just for numbering/counting the tweets.
             #       Number inside [ ] is the
             #       the number/position of tweet inside the original json file. Used
             #       as a reference to link back to the original.           
             print((numProcessed - numRetweets), ") [", i,"] ", tweetUrl, " (",
                   jsonData['data'][i]['referenced_tweets'][0]['type'], ")", sep="" )
    else:
        tweetUrl =  "https://twitter.com/i/web/status/" + jsonData['data'][i]['id']
        if jsonData['data'][0]['author_id'] in userObs.keys():
           msg = userObs[jsonData['data'][i]['author_id']]['username']
        else:
           msg = 'user NOT found'
        print((numProcessed - numRetweets), ") [",i,") ", tweetUrl, " {", msg, "}", sep="" )
        
        #https://twitter.com/i/web/status/
print('Total tweets:', totalTweets, " Retweets:", numRetweets)
        


