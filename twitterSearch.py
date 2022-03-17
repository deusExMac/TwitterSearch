# How to use Twitter's v2 API to searcha nd download for tweets.
# IMPORTANT! In order to properly execute this program, you'll need
#            to create a Twitter developer account and get an access and bearer token.
#
# The developed was dased on the source code found here:
#    https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
#
# TODO: This has been created in a hurry. Needs serious refactoring.
#
# v0.4b mmtrd31/12/2021



#For sending REST requests to the API Endpoint
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API

import sys

import json

# For saving the response data in CSV format
import csv
# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
from datetime import datetime, timedelta
import unicodedata

#To add wait time between requests
import time

import configparser
import os.path

import pprint
import argparse


# We define constants in this file
import appConstants
from commandHistory import commandHistory
import twitterV2API 

# For testing only
import utils

class ArgumentParserError(Exception): pass
  
class ThrowingArgumentParser(argparse.ArgumentParser):
      def error(self, message):
          raise ArgumentParserError(message)




def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def create_url(keyword, start_date, end_date, max_results = 10, cfg=None):
    
    # NOTE: /2/tweets/search/recent is the recent endpoint!
    #search_url = "https://api.twitter.com/2/tweets/search/recent" #Change to the endpoint you want to collect data from

    search_url = cfg.get('TwitterAPI', 'apiEndPoint', fallback="")

    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)


def connect_to_endpoint(url, headers, params, next_token = None):
    #params object received from create_url function
    params['next_token'] = next_token   
    response = requests.request("GET", url, headers = headers, params = params)
    #print("\tEndpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()



#
# This needs to be rewritten...
#
def append_to_csv(json_response, fileName, sep, extypes, nTweets = 0, mxTweets = -1):
    
    # Iterate over user objects
    userObs = {}
    totalUsers = len(json_response['includes']['users'])
    for k in range(totalUsers):
        userObs[json_response['includes']['users'][k]['id']] = json_response['includes']['users'][k]

    #A counter variable
    counter = 0

    # Counting the type of tweets
    numRetweets = 0
    numRepliedTo = 0
    numQuoted = 0
    
    excludeTweets = extypes.split(',') #cfg.get('Storage', 'excludeTweetsType', fallback=' ').split(',')
    
    #Open OR create the target CSV file
    if not os.path.exists(fileName):
      csvFile = open(fileName, "w", newline="", encoding='utf-8')
      csvWriter = csv.writer(csvFile, delimiter=sep) # TODO: , delimiter= cfg setting...      
      csvWriter.writerow(['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','source','tweet', 'tweettype', 'username', 'tweetcount', 'followers', 'following'])
    else:      
      csvFile = open(fileName, "a", newline="", encoding='utf-8')
      csvWriter = csv.writer(csvFile, delimiter=sep) # TODO: , delimiter= cfg setting...

    

   #delimiter=cfg.get('Storage', 'csvSeparator', fallback=',')
    
    #Loop through each tweet
    for tweet in json_response['data']:

        tweet_type = "" 
        if 'referenced_tweets' in tweet:
            tweet_type =  tweet['referenced_tweets'][0]['type']
            if tweet_type == "retweeted":
               numRetweets += 1
            elif tweet_type == "quoted":
                 numQuoted += 1
            elif tweet_type == "replied_to":
                 numRepliedTo += 1
            if tweet['referenced_tweets'][0]['type'] in excludeTweets:
               #print("X (", tweet['referenced_tweets'][0]['type'],")", sep="", end="" )
               continue
            
        # We will create a variable for each since some of the keys might not exist for some tweets
        # So we will account for that

        # 1. Author ID
        author_id = tweet['author_id']

        # TODO: make sure these exist!
        authorName = userObs[author_id]['username']
        authorFollowers = userObs[author_id]['public_metrics']['followers_count']
        authorFollowing = userObs[author_id]['public_metrics']['following_count']
        authorTweetCount = userObs[author_id]['public_metrics']['tweet_count']

        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Geolocation
        geo = " "
        if ('geo' in tweet):
            if 'place_id' in tweet['geo']:
                geo = tweet['geo']['place_id']
        
            

        # 4. Tweet ID
        tweet_id = tweet['id']

        # 5. Language
        lang = tweet['lang']

        # 6. Tweet metrics
        #
        # TODO: make sure these exist in the historic archive also
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 7. source
        source = ''
        if 'source' in tweet.keys():
            source = tweet['source']
                    
            
        # 8. Tweet text
        text = tweet['text']
          
        # mmt: do some preprocessing before storing to file
        #
        # TODO: Fixme!
        text = text.replace("\n", " ")
        text = text.replace( "\t", " " )
        text = text.replace( sep, " " )        
        text = text.replace( "\"", " " )
        text = text.replace( "'", " " )
       
        
        # Assemble all data in a list
        res = [author_id, created_at, geo, tweet_id, lang, like_count, quote_count, reply_count, retweet_count, source, text, tweet_type, authorName, authorTweetCount, authorFollowers, authorFollowing]
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1
        nTweets += 1
        if mxTweets > 0:
           if nTweets >= mxTweets:
              break 

    # When done, close the CSV file
    csvFile.close()
    return(counter)
    # Print the number of tweets for this iteration
    #print("\t# of Tweets added from this response: ", counter) 


def saveToFile(rsp, batchCount=1):
    f = open("jsonResponse-Example-" + str(batchCount) + ".txt", "w", encoding='utf-8')
    json.dump(rsp, f, ensure_ascii=False, indent=4)
    #json.dump(rsp, f)
    f.close()



def log(logF, m):
    with open(logF, 'a') as lF:
         lF.write('[' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '] ' + m + '\n')





def doSearch( q, dateFrom, dateTo, timeStep, cfg=None):

    if q.strip() == '':
       print('Error: Empty query.')
       print('Usage: search [-f <start date of tweets>] [-u <end date of tweets>] [-t <subperiod breakup specifications>] [-n <number of tweets to fetch each period>] [-o <csv file name to store fetched tweets>] <query>')
       return(None)

    
    searchPeriods = []
    pAdded = generatePeriods( dateFrom, dateTo, timeStep, searchPeriods, cfg)
    if pAdded is None:
       print("Error adding periods")
       return(None)

    return( searchTweets(q, searchPeriods, cfg) )



def searchTweets(q, datePeriods=None, cfg=None):


    print("\nCommencing tweet search")
    print("Search parameters:")
    print("\tQuery:", q)
    print("\tTarget archive:", cfg.get('TwitterAPI', 'targetArchive', fallback="recent") )
    print("\tNumber of search periods:", len(datePeriods))
    print("\tMaximum number of tweets to fetch in each period:",  cfg.get('General', 'maxTweetsPerPeriod', fallback="30"))
    print("\tNumber of tweets to ask from endpoint per request:",  cfg.getint('TwitterAPI', 'maxEndpointTweets', fallback=100) )
    print("\tTweets saved to csv file:",  cfg.get('Storage', 'csvFile', fallback="data.csv"), "\n" ) 

    time.sleep( 2.3 )


    headers = create_headers(  cfg.get('TwitterAPI', 'Bearer', fallback='') )    

    max_results = cfg.getint('TwitterAPI', 'maxEndpointTweets', fallback=100) #100
    total_tweets = 0
    batchCount = 0

    # Total number of tweets to fetch across all periods
    maxTotalTweets = cfg.getint('General', 'maxTweets', fallback=1000) #400
    max_count = cfg.getint('General', 'maxTweetsPerPeriod', fallback=30 ) #maxPeriodTweets # Max tweets per time period

    for i in range(len(datePeriods)):

        log( configSettings.get('Debug', 'logFile', fallback="app.log") ,
             "Getting [" + cfg.get('General', 'maxTweetsPerPeriod', fallback='30' ) + "] tweets for period [" + datePeriods[i]['from'] + "] until [" + datePeriods[i]['until'] +"]")
        
        
        print(">>> Period [", datetime.strptime(datePeriods[i]['from'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S'), " - ", datetime.strptime(datePeriods[i]['until'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S'), "] : Getting a maximum of [", cfg.get('General', 'maxTweetsPerPeriod', fallback='30' ),"] tweets for this period", sep="")
        count = 0 # Counting tweets per time period        
        flag = True
        moreResults = True
        next_token = None

        while moreResults:
           if max_count > 0:
             if count >= max_count:
                log( configSettings.get('Debug', 'logFile', fallback="app.log") , "Period [" + datePeriods[i]['from'] + " - " + datePeriods[i]['until'] + "] Stopping due to max period number of tweets [" + str(max_count) + "] reached.")
                print(" (LR p:", count, ", t:",total_tweets,")")
                break 

           try:
              url = create_url(q, datePeriods[i]['from'],datePeriods[i]['until'], cfg.getint('TwitterAPI', 'maxEndpointTweets', fallback=100), cfg)
              json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
           except Exception as ex:
              log( configSettings.get('Debug', 'logFile', fallback="app.log") , "Period [" + datePeriods[i]['from'] + " - " + datePeriods[i]['until'] + "] Twitter endpoint error. Message:" + str(ex) )              
              print(str(ex))              
              sys.exit("\nFaral error. Terminating. Sorry.\n")

                      
           result_count = json_response['meta']['result_count']
           
              
           if result_count is not None and result_count > 0:
              twWritten = append_to_csv(json_response, cfg.get('Storage', 'csvFile', fallback="data.csv"), cfg.get('Storage', 'csvSeparator', fallback=','), cfg.get('Storage', 'excludeTweetsType', fallback=' '), count, max_count)
              count += twWritten              
              total_tweets += twWritten
              if cfg.getboolean('Debug', 'showProgress', fallback=False):
                print("(f:", result_count, ", t:", total_tweets, ")", sep="", end="")
              else:
                print(".", end="")
              
              #print("(S:", twWritten, "/",result_count, ")", end="")

           if 'next_token' in json_response['meta']:
              # Save the token to use for next call
              next_token = json_response['meta']['next_token']

              #sleep, but a shorter amount
              time.sleep( cfg.getfloat('Request', 'sleepTime', fallback=3.8) / 2.0 )
           else:
               moreResults = False
               next_token = None
               log( configSettings.get('Debug', 'logFile', fallback="app.log") , "Period [" + datePeriods[i]['from'] + " - " + datePeriods[i]['until'] + "] Stopping due no more next tokens.")
               print("(NT p:", count, ", t:",total_tweets,")")

        # Sleep to avoid bombarding server
        time.sleep( cfg.getfloat('Request', 'sleepTime', fallback=3.8) )      

    print("Total number of tweets collected: ", total_tweets)
    return( total_tweets )




def doParse(cmdArgs):
    
    #prms = {'keywords':'', 'lang':'', 'from':'', 'until':'', 'stepD': 0, 'stepH': 0, 'stepM':0, 'stepS':0, 'user':''}
   try:  
    parser = ThrowingArgumentParser()
    #datetime.now().strftime("%d/%m/%Y")
    parser.add_argument('-f', '--from',   nargs='?', default= (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y") )
    parser.add_argument('-u', '--until', nargs='?', default=(datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y") )
    parser.add_argument('-t', '--timestep', nargs='?', default="" )
    parser.add_argument('-n', '--numtweets', type=int, nargs='?', default=0 )
    parser.add_argument('-o', '--outfile', type=str, nargs='?', default='' )
    parser.add_argument('-D',  '--debugmode', action='store_true')

    # IMPORTANT! arguments -f, -u -t -n etc on the command line, MUST APPEAR BEFORE
    #            the remaining arguments. Otherwise, these arguments will not be parsed
    #            and will be part of the ramaining arguments.
    parser.add_argument('keywords', nargs=argparse.REMAINDER)
    
    #parser.add_argument('-s', '--startpos', type=int,   nargs='?', default=0)
    #parser.add_argument('-v',  action='store_true')
    #parser.add_argument('-O', '--overwritefile',   action='store_true', default=False)         
    #parser.add_argument('-o', '--outputfile',   nargs='?')
    #parser.add_argument('-S', '--skipfetched',   action='store_true', default=False)
    
         
    
    args = vars( parser.parse_args(cmdArgs) )

    # We make sure that no . spearator (separating seconds from ms at the end is present (as return by now())
    # this will destroy all our hypotheses about the formatting.
    # Dates are always returned in isoformat.
    args['from'] = dateutil.parser.parse( args['from'].split('.')[0] , dayfirst=True).isoformat() + 'Z'        
    args['until'] = dateutil.parser.parse( args['until'].split('.')[0] , dayfirst=True).isoformat() + 'Z'    
    return(args)
    
   except Exception as argEx:
      print( str(argEx) ) 
      #print("EEE Usage: <TODO: Fill me>")
      return(None)      


   return(None)




def parseSearchQuery(qList):


    return(doParse(qList))
    
    qryParams = {'keywords':'', 'lang':'', 'from':'', 'until':'', 'stepD': 0, 'stepH': 0, 'stepM':0, 'stepS':0, 'user':''}
    for tk in qList:
        if tk.lower().startswith('lang:'):
            qryParams['lang'] = tk[5:]
        elif tk.lower().startswith('from:'):
            try:
               dtStr = tk[5:].replace('@', ' ') 
               qryParams['from'] = dateutil.parser.parse(dtStr, dayfirst=True).isoformat() + 'Z'
            except:
               print("Invalid from date") 
               return(None) 
        elif tk.lower().startswith('until:'):
           try:
              dtStr = tk[6:].replace('@', ' ')  
              qryParams['until'] = dateutil.parser.parse(dtStr, dayfirst=True).isoformat() + 'Z'
           except:
               print("Invalid to date")
               return(None)
        elif tk.lower().startswith('step:'):
              if 'H' not in tk[5:] :
                  tVal = tk[5:] + "0H0M0S"
              elif 'M' not in tk[5:] :
                  tVal = tk[5:] + "0M0S"
              elif 'S' not in tk[5:]:
                  tVal = tk[5:] + "0S"
              else:
                  tVal = tk[5:]


              tVal = tVal.strip()
              
              # IMPORTANT! We'll be using strptime to quickly parse the
              # kind of date format in the form xDyHzMkS. that means that not all
              # integer values are accepted. I.e. value for days can be between 1 and 31.
              # That's not 
              # TODO: Change to allow any valid step for Days, Hours, Minutes and Seconds.
              #
              # There is an issue if 0D (i.e. zero days) is in the date. strptime does not
              # consider it a valid value. 0 minutes or secongs are valid though.
              # We go around this by doing some additional checks (FIXED: on 17/02/2022.
              # Using .startswith now to avoid misinterpretations.)            
              zeroDays = False
              if tVal.startswith('0D'):
                  tVal = tVal.replace('0D', '') # TODO: Fix me! This will also replace 10DXXXX and that's not good!
                  tmFormat = '%HH%MM%SS'
                  zeroDays = True
              else:              
                  tmFormat = '%dD%HH%MM%SS'
              
              try:                 
                 diffT =  datetime.strptime(tVal, tmFormat)

                 if not zeroDays:
                    qryParams['stepD'] = diffT.day
                    
                 qryParams['stepH'] = diffT.hour
                 qryParams['stepM'] = diffT.minute
                 qryParams['stepS'] = diffT.second
              except Exception as ex:
                 print( "Invalid date step ", str(ex))
                 return(None)
                
        elif tk.lower().startswith('user:'):
             qryParams['user'] = tk[5:]              
        else:
            qryParams['keywords'] = qryParams['keywords'] + " " + tk

    return(qryParams)
           




def generatePeriods( f, u, t, tPeriods, cfg=None):

    if datetime.strptime(f, "%Y-%m-%dT%H:%M:%SZ") > datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ"):
       print('Invalid dates: End-date [', u, '] must be after start-date [', f, ']') 
       return(None)
      
    if t == "":
       tPeriods.append( {'from': f, 'until': u} )
       if cfg.getboolean('Debug', 'debugMode', fallback=False):  
          print("\t[DEBUG] No time step specified. Adding SINGLE search period: [", datetime.strptime(f, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M:%S"), "-", datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M:%S"), "]")

       return(1)

    # Do some normalization if needed
    if 'D' not in t:
        return(None)
    
    if 'H' not in t:
        t += '0H0M0S'
    elif 'M' not in t:
          t += '0M0S'
    elif 'S' not in t:
          t +='0S'

    #parse time period step
    dayVal = -1 # Days are handled in a special way because we use existing date parsing routines and number of days cannot be 0 or exceed 31    
    if t.startswith('0D'):
       t = t.replace('0D', '')
       tmFormat = '%HH%MM%SS'
       dayVal = 0
    else:
        tmFormat = '%dD%HH%MM%SS'

    try: 
        stepValue =  datetime.strptime(t, tmFormat)
        if dayVal != 0:
           dayVal = stepValue.day 
    except Exception as sEx:
        print( "Invalid time step ", str(sEx))
        return(None)
        
    
    sDate = datetime.strptime(f, "%Y-%m-%dT%H:%M:%SZ")
    pCnt = 0
    while True:
        eDate = sDate + timedelta(days= dayVal, hours = stepValue.hour, minutes = stepValue.minute, seconds=(stepValue.second) )                                                            
        if eDate >= datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ"):
           eDate = datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ")
           tPeriods.append( {'from': sDate.strftime("%Y-%m-%dT%H:%M:%SZ"), 'until': eDate.strftime("%Y-%m-%dT%H:%M:%SZ")} )
           pCnt += 1
           if cfg.getboolean('Debug', 'debugMode', fallback=False):
              print("\t[DEBUG] Adding search period: [", sDate.strftime("%d/%m/%Y %H:%M:%S"), "-", eDate.strftime("%d/%m/%Y %H:%M:%S"), "]")
              
           return(pCnt)
      
        if cfg.getboolean('Debug', 'debugMode', fallback=False):
           print("\t[DEBUG] Adding search period: [", sDate.strftime("%d/%m/%Y %H:%M:%S"), "-", eDate.strftime("%d/%m/%Y %H:%M:%S"), "]")
           
        tPeriods.append( {'from': sDate.strftime("%Y-%m-%dT%H:%M:%SZ"), 'until': eDate.strftime("%Y-%m-%dT%H:%M:%SZ")} )
        pCnt += 1
        sDate = sDate + timedelta(days= dayVal, hours = stepValue.hour, minutes = stepValue.minute, seconds=stepValue.second)

    return(pCnt)





def displayConfigSettings(cs):
    print("Configuration settings")
    for s in cs.sections():
        print("Section [", s, "]", sep="")
        for key, value in cs[s].items():
            print( "\t-", key, "=", value)


def setTargetArchive(cfg, md):
    if md.lower() == "recent":
       if 'TwitterAPI' in cfg.sections(): 
           cfg['TwitterAPI']['apiEndPoint'] =  cfg['TwitterAPI']['recentApiEndPoint']
           cfg['TwitterAPI']['bearer'] =  cfg['TwitterAPI']['essentialBearer']
           cfg['TwitterAPI']['targetArchive'] = 'recent'
           print("Target archive set to recent.")
    elif  md.lower() == "historic":
          cfg['TwitterAPI']['apiEndPoint'] =  cfg['TwitterAPI']['historicApiEndPoint']
          cfg['TwitterAPI']['bearer'] =  cfg['TwitterAPI']['academicBearer']
          cfg['TwitterAPI']['targetArchive'] = 'historic'
          print("Target archive set to historic.")
    else:
          print("Invalid target archive option [", md, "]. Use historic or recent")

        
# TODO: Complete me
def printHelp():
    print("Supported commands and their syntax:")
    print("")
    print('\tsearch [-f <date>] [-u <date>] [-t <time step>] [-D] [-o <csv file>] [-n <number of tweets/period>] <query>')
    print('\tAbout:')
    print( NLprint('| Searches for tweets containing <query> published between dates specified in -f (from) and -u (until). If -t option is specified then the date range is divided in subranges according to the format specified by -t and search is conducted separately in each subrange. -n specifies how many') ) 
    print("\t* search [-f <date>] [-u <date>] [-t <time step>] [-D] [-o <csv file>] [-n <number of tweets/period>] <query>: searches for tweets containing <query> published",
          "between dates specified in -f (from) and -u (until). If -t option is specified then the date range is divided in subranges according to the format specified by -t and search is conducted separately in each subrange. -n specifies how many" ,
          "tweets to download during each subperiod. -o specifies the csv file to store tweets that meet the conditions. -D toggles the current debug mode on or off. Enter datetimes as follows Day/Month/Year@Hour:Minutes:Seconds.Milliiseconds . Datetimes are always in UTC. Example: search covid19 lang:en from:29/12/2021@10:07:55 until:31/12/2021@08:32:11.210")
    print("\t* config: display configuration settings that have been loaded")
    print("\t* set <section> <setting/key> <new value>: update loaded configuration setting/key <setting/key> in <section> to new value <new value>. Does not affect loaded configuration file.")
    print("\t* set target <historic | recent> : Set on which archive to search. Will change endpoint and bearer token.")
    print("\t* addperiod from:<date> until:<date> step:<amount>: add a period to search for keywords. If step is given, this specifies the period will be broken down in smaller periods of length specified by step.")
    print("\t* clearperiods : clear all periods")
    
    print("\t* history : a list of previous commands (command history list) given using the interface (for reuse).")
    print("\t* !<index> : execute command at position <index> in the command history list. ")
    print("\t* quit : Terminate application and quit.")
    
    print("\t* help : This screen.")
    print("")



def NLprint(string, every=72):
    lines = []
    for i in range(0, len(string), every):
        lines.append('\t' + string[i:i+every])
    return '\n'.join(lines)





#
# IGNORE the next line if you are NOT A MacOS user with an older version of
# Python 3.x.x :
#
# sys.argv = [sys.argv[0], '-c', 'sensitiveFiles/twitterSearch.conf']


######################################################################
#
# Program starts here
#
######################################################################


cmdArgParser = argparse.ArgumentParser(description='Command line arguments')
cmdArgParser.add_argument('-c', '--config',   default=appConstants.DEFAULTCONFIGFILE)
args = vars( cmdArgParser.parse_args() )

# Config file that will be used
configFile = args['config']

      
print("")        
print('v'+appConstants.APPVERSION, 'rd', appConstants.VERSIONRELEASEDATE )

# Note: We use .RawConfigParser() because some configuration strings contain special chars like % that
#       have special meaning for the ConfigParser class
configSettings = configparser.RawConfigParser(allow_no_value=True)

 


# Load config file
if os.path.exists(configFile):    
   configSettings.read(configFile)
   configSettings.add_section('__Runtime')
   configSettings['__Runtime']['__configSource'] = configFile
   print("Loaded configuration file ", configFile, sep="")
else:
   configSettings.add_section('__Runtime')
   configSettings['__Runtime']['__configSource'] = ''
   print("Configuration file [", configFile, "] not found. Continuing with default settings.", sep="")


    



print("Type 'help' to see a list of supported commands.\n")
setTargetArchive(configSettings, configSettings.get('TwitterAPI', 'targetArchive', fallback="recent") )

# Create a v2 Twitter search API instance. This is our gateway to search and access the tweets
tAPI = twitterV2API.twitterSearchClient(configSettings)
# Create a history object
cHistory = commandHistory(configSettings.getint('Shell', 'historySize', fallback=10), True)



# Simple command line interface to
# play around with Twitter API v2
#
#16/02/2022: Needs to be refactored. Is ugly. Have been
#            adding functionality quick and dirty. No extensive testing too. Sorry!  
while True:

  try:  
    command = input(configSettings.get('General', 'commandPrompt', fallback="(default conf) >>> ") )
    command = command.strip()
    
    if len(command) == 0:
       continue


    if command.strip() == '!!':
       command = cHistory.getLast()
       print('[', command, ']')
       
          
    if command.startswith('!'):
       try:
          command = cHistory.get( int(command[1:]) )
          if command == '':
             continue             
       except:
          print("Invalid index", command[1:]) 
          continue
       
       print("[", command, "]\n")


    if command == '':
       continue   
        
    if command.lower() not in ['history', 'h', 'quit', 'q']:           
           cHistory.addCommand( command )
    
    cParts = command.split()
    
    if cParts[0].lower() == "newsearch":
        
        qr = parseSearchQuery(cParts[1:])
        if qr is None:
          print("Usage:search -f <from date> -u <to date> -n <number of tweets> query")
          continue


        if qr['numtweets'] != 0:
           configSettings['General']['maxTweetsPerPeriod'] =  str(qr['numtweets'])


        if qr['outfile'] != '':
            if configSettings.getboolean('Debug', 'debugMode', fallback=False):
               print("[DEBUG] Overriding setting csvFile from [", configSettings['Storage']['csvFile'], "] to [", qr['outfile'], "]")
             
            configSettings['Storage']['csvFile'] =  qr['outfile']

        # Save old value. We get it as a string value as configurations do not support
        # boolean values (i.e. everything is a string).
        oldVal = configSettings.get('Debug', 'debugMode', fallback='false')
        
        if qr['debugmode']:
            #if configSettings.getboolean('Debug', 'debugMode', fallback=False):
            print("[DEBUG] Overriding setting debugMode from [", configSettings['Debug']['debugMode'], "] to [", str(not configSettings.getboolean('Debug', 'debugMode', fallback=False)), "]")
            # toggle debug setting
            configSettings['Debug']['debugMode'] =  str( not configSettings.getboolean('Debug', 'debugMode', fallback=False)) #str(qr['debugmode'])   
  
        nFetched = tAPI.query( qr['from'], qr['until'], qr['timestep'], " ".join(qr['keywords']).strip() ) 
        if nFetched >= 0:
           print('Fetched total of', nFetched, 'tweets.')
        else:
           print('Error ', nFetched, 'encounterred.')   

        
        if configSettings.getboolean('Debug', 'debugMode', fallback=False):
           print('[DBUG] Setting debugMode back to [', oldVal, ']')

        # Restore old value    
        configSettings['Debug']['debugMode'] = oldVal
        
    elif cParts[0].lower() == "search":
         
         qr = parseSearchQuery(cParts[1:])
         if qr is None:
          print("Usage:search -f <from date> -u <to date> -n <number of tweets> query")
          continue

         if qr['numtweets'] != 0:
          if configSettings.getboolean('Debug', 'debugMode', fallback=False):
             print("[DEBUG] Overriding setting maxTweetsPerPeriod from [", configSettings['General']['maxTweetsPerPeriod'], "] to [", qr['numtweets'], "]")
             
          configSettings['General']['maxTweetsPerPeriod'] =  str(qr['numtweets'])

         if qr['outfile'] != '':
            if configSettings.getboolean('Debug', 'debugMode', fallback=False):
               print("[DEBUG] Overriding setting csvFile from [", configSettings['Storage']['csvFile'], "] to [", qr['outfile'], "]")
             
            configSettings['Storage']['csvFile'] =  qr['outfile']

         
         if qr['debugmode']:
            #if configSettings.getboolean('Debug', 'debugMode', fallback=False):
            print("[DEBUG] Overriding setting debugMode from [", configSettings['Debug']['debugMode'], "] to [", qr['debugmode'], "]")

            configSettings['Debug']['debugMode'] =  str(qr['debugmode'])
          
         nTweets = doSearch(" ".join(qr['keywords']).strip(), qr['from'], qr['until'], qr['timestep'], configSettings )

         # 
         # TODO: Set  debugmode to old value if needed.
         #

    elif cParts[0].lower() == "quit" or cParts[0].lower() == "q":
         break
    elif cParts[0].lower() == "config" or cParts[0].lower() == "settings":
         displayConfigSettings(configSettings)
    elif cParts[0].lower() == "set":

         if cParts[1] == "target":
            setTargetArchive(configSettings, cParts[2])
            continue
             
         if len(cParts) < 4:
            print("Usage: set <section name> <parameter> <new value>")
         else:              
              if cParts[1] != 'DEFAULT' and (cParts[1] not in configSettings.sections()):
                 print("Usage: set <section name> <parameter> <new value>")
              else:   
                 configSettings[cParts[1]][cParts[2]] = cParts[3]
    elif cParts[0].lower() == "help":
         printHelp() 
    elif cParts[0].lower() == "addperiod":

         cmdParams = parseSearchQuery(cParts[1:])
         pDs = utils.generateSubperiods(cmdParams['from'], cmdParams['until'], cmdParams['timestep'], configSettings)
         if pDs is None:
            print('Error. No periods created')
         
         
    
    elif cParts[0].lower() == "h" or cParts[0].lower() == "history":
         cHistory.printHistory() 
         
    elif cParts[0].lower() == 'reload':
          
         shellParser = ThrowingArgumentParser()
         
         try:
           shellParser.add_argument('-c', '--config',   nargs='?', default='')
           shellArgs = vars( shellParser.parse_args( cParts[1:] ) )
         except Exception as ex:
             print("Invalid argument. Usage: reload [-c config_file]")
             continue
               
         if  shellArgs['config'] == '':
             configFile = configSettings['__Runtime']['__configSource']
         else:
             configFile = shellArgs['config']
             
         
         if configFile == '':
            print('No configuration file. No configuration loaded.')   
            continue

         if not os.path.exists(configFile):
            print('Configuration file [', configFile ,'] not found', sep='')
            print('No configuration file loaded.')
            continue

         print('Loading configuration file: [', configFile, ']', sep="")
         configSettings = configparser.RawConfigParser(allow_no_value=True)
         configSettings.read(configFile)
         configSettings.add_section('__Runtime')
         configSettings['__Runtime']['__configSource'] = configFile
         print("Configuration file [", configFile, "] successfully loaded.", sep="")

         # Make sure that the target and bearer agree
         setTargetArchive(configSettings, configSettings.get('TwitterAPI', 'targetArchive', fallback="recent") )

         tAPI.setConfiguration( configSettings )
         
    else:
        print("Unknown command:", cParts[0])

  except KeyboardInterrupt:
       print("\nKeyboard interrupt seen.")
       
cHistory.save()
print("\nFinished. ByeBye!")



