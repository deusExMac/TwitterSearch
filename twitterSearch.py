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



    
class shellCommandExecutioner:

      def __init__(self, cfg):
          self.configuration = cfg
          self.totalCommands = 0
          self.commandsExecuted = 0

          
      def shellExecute( self, commandParts):
          #default = 'Invalid command ' + commandParts[0] + '. Type help for a list of supported commands.'
          #print('Shell execute [', commandParts[0], ']', sep='')
          self.totalCommands += 1  
          if not hasattr(self, commandParts[0]):
             self.defaultF(commandParts[0])
             return(False)
            
          self.commandsExecuted += 1
          return getattr(self, commandParts[0])(commandParts[1:])  



      def displayConfigSettings(self):
         if self.configuration is None:
            print('No configuration.')
            return
      
         print("Configuration settings")
         for s in self.configuration.sections():
             print("Section [", s, "]", sep="")
             for key, value in self.configuration[s].items():
                 print( "\t-", key, "=", value)




      def defaultF(self, a):
          print('Invalid command', a)


      def q(self, a):
          return( True )
      
      def quit(self, a):
          return( True )
      
      
      def config(self, a):
          print('Executing config')
          self.displayConfigSettings()
          return(False)


      def search(self, a):
          print('Executing search')
          sParams = parseCommandArguments(a)
          if sParams is None:
             print("Usage: search [-f <from date>] [-u <to date>] [-n <number of tweets>] [-o <csv file>] [-D] <query>")
             return(False)


          if sParams['numtweets'] != 0:
             self.configuration['General']['maxTweetsPerPeriod'] =  str(sParams['numtweets'])


          if sParams['outfile'] != '':
            if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
               print("[DEBUG] Overriding setting csvFile from [", self.configuration['Storage']['csvFile'], "] to [", sParams['outfile'], "]")
             
            self.configuration['Storage']['csvFile'] =  sParams['outfile']

          # Save old value. We get it as a string value as configurations do not support
          # boolean values (i.e. everything is a string).
          oldVal = self.configuration.get('Debug', 'debugMode', fallback='false')
        
          if sParams['debugmode']:
            #if configSettings.getboolean('Debug', 'debugMode', fallback=False):
            print("[DEBUG] Overriding setting debugMode from [", self.configuration['Debug']['debugMode'], "] to [", str(not self.configuration.getboolean('Debug', 'debugMode', fallback=False)), "]")
            # toggle debug setting
            self.configuration['Debug']['debugMode'] =  str( not self.configuration.getboolean('Debug', 'debugMode', fallback=False)) 



          # Perform actual search for tweets with the parameters given.
          tAPI = twitterV2API.twitterSearchClient(self.configuration)
          nFetched = tAPI.query( sParams['from'], sParams['until'], sParams['timestep'], " ".join(sParams['keywords']).strip() ) 
          if nFetched >= 0:
             print('Fetched total of', nFetched, 'tweets.')
          else:
             print('Error ', nFetched, 'encounterred.')   

        
          if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
             print('[DBUG] Setting debugMode back to [', oldVal, ']')

          # Restore old value    
          self.configuration['Debug']['debugMode'] = oldVal
          return(False)




      # TODO: Sorry about this. It's a mess. Needs to be seriously refactored.
      #       This was done quickly.
      def help(self, a):
            print("\n\tSupported commands and their syntax:")
            print("")
            print('\t' + 72*'-')
            print( NLFormat('search [-f <date>] [-u <date>] [-t <time step>] [-D] [-o <csv file>] [-n <number of tweets/period>] <query>', 72) )
            print('\t'+72*'-')
            print('\tAbout:')
            print( NLFormat('     Performs a period search. Searches for tweets meeting conditions in <query> published between the dates specified in -f (from) and -u (until) arguments which is called a period. If -t , -u are missing, default date range is [two days ago - yesterday].  For a list of supported query operators see: https://developer.twitter.com/en/docs/twitter-api/v1/rules-and-filtering/search-operators . If -t option is specified then' +
                         ' the date range is divided into subranges according to the format specified by -t and search is conducted separately in each subrange. -n specifies how many' +
                         ' tweets to download during each subperiod. -o specifies the csv file to store tweets that meet the conditions. -D toggles the current debug mode on or off.'))
            print( NLFormat( "-f, -u: Datetimes should be enterred as Day/Month/YearTHour:Minutes:Seconds. Datetimes are always in UTC. Example: search -f 29/12/2021T10:07:55 -u 31/12/2021T08:32:11 euro crisis" ))
            print( NLFormat( "-t: Time steps should be specified in the following manner: kDmHnMzS where k, m, n and z integer values. Example 3D10H5M8S. -t format specifies how the date range specified " +
                          " by -f and -u arguments will be divided into subperiods, in each of which a seperate search will be conducted for the same query. For example the query search -f 3/2/2008 -u 10/2/2008 -t 2D10H5M2S euro " +
                          " will break up the date range [3/2/2008, 10/2/2008] to subperiods of length 2 days, 10 hours, 5 minutes and 2seconfs and conduct a search in each of these perids. In this example, search " +
                          "for the term euro in tweets will be conducted in the following periods separately:"))
            print( NLFormat('[ 03/02/2008 00:00:00 - 05/02/2008 10:05:02 ]'))
            print( NLFormat('[ 05/02/2008 10:05:02 - 07/02/2008 20:10:04 ]'))
            print( NLFormat('[ 07/02/2008 20:10:04 - 10/02/2008 00:00:00 ]'))
            print("")
            print('\t' + 72*'-')
            print( NLFormat('config') )
            print('\t' + 72*'-')
            print('\tAbout:')
            print( NLFormat('Displays currently loaded configuration settings.'))
            print("")
            print('\t' + 72*'-')
            print( NLFormat('reload [-c <path to configuration file>]') )
            print('\t' + 72*'-')
            print('\tAbout:')
            print( NLFormat('Allows loading a configuration file specified by the -c option. Relating file names are supported. In no -c option is provided, the config file loaded during startup is reloaded.'))                
            print('')
            print('\t' + 72*'-')
            print( NLFormat('history (alternatively h)' ) )
            print('\t' + 72*'-')
            print('\tAbout:')
            print( NLFormat('Displays a numbered list of the history of commands executed. Numbers can be used with ! (see below). Usefull to re-execute commands or copy-paste complicated commands'))
            print('')
            print('\t' + 72*'-')
            print( NLFormat('set [-G | --target <historic | recent>]' ) )
            print('\t' + 72*'-')
            print('\tAbout:')
            print( NLFormat('Specifies in which archive the search should be condicted. Value recent means that search is limited to tweets published the last 5 days. Value historic means that one may specify any time period without any constraint.' +
                          'Value recent and historic use different bearer tokens and hence tweets are accounted in different developer accounts. You get bearer tokens freely. recent bearer tokens are obtained by ' +
                          'simply opening a developer account. Search in the historic archive requires an academic bearer token that you can request.'))
            print('')
            print('\t' + 72*'-')
            print( NLFormat('!<index>' ) )
            print('\t' + 72*'-')
            print('\tAbout:')
            print( NLFormat('Execute command at the position <index> in the command history list (see history or h).'))
            print('')
            print('\t' + 72*'-')
            print( NLFormat('!!' ) )
            print('\t' + 72*'-')
            print('\tAbout:')
            print( NLFormat('Re-executes last command.'))
            print('')
            print('')
            print('\t' + 72*'-')
            print( NLFormat('help' ) )
            print('\t' + 72*'-')
            print('\tAbout:')
            print( NLFormat('This screen.'))
            print('')
            print('\t' + 72*'-')
            print( NLFormat('quit or q' ) )
            print('\t' + 72*'-')
            print('\tAbout:')
            print( NLFormat('Terminates and quits the application.'))
            print('')

            print('')




      def set(self, a):
          shellParser = ThrowingArgumentParser()
          try:
           shellParser.add_argument('-G', '--target',   nargs='?', default='recent')
           shellArgs = vars( shellParser.parse_args( a ) )
          except Exception as ex:
             print("Invalid argument. Usage: set [-G] value")
             return(False)

          setTargetArchive(self.configuration, shellArgs['target'])



  
      def reload(self, a):
        shellParser = ThrowingArgumentParser()         
        try:
           shellParser.add_argument('-c', '--config',   nargs='?', default='')
           shellArgs = vars( shellParser.parse_args( a ) )
        except Exception as ex:
             print("Invalid argument. Usage: reload [-c config_file]")
             return(False)
               
        if  shellArgs['config'] == '':
          configFile = self.configuration['__Runtime']['__configSource']
        else:
          configFile = shellArgs['config']
             
         
        if configFile == '':
          print('No configuration file. No configuration loaded.')   
          return(False)

        if not os.path.exists(configFile):
          print('Configuration file [', configFile ,'] not found', sep='')
          print('No configuration file loaded.')
          return(False)

        print('Loading configuration file: [', configFile, ']', sep="")
        self.configuration = configparser.RawConfigParser(allow_no_value=True)
        self.configuration.read(configFile)
        self.configuration.add_section('__Runtime')
        self.configuration['__Runtime']['__configSource'] = configFile
        print("Configuration file [", configFile, "] successfully loaded.", sep="")

        # Make sure that the target and bearer agree
        setTargetArchive(self.configuration, self.configuration.get('TwitterAPI', 'targetArchive', fallback="recent") )





'''
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

'''




def log(logF, m):
    with open(logF, 'a') as lF:
         lF.write('[' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '] ' + m + '\n')





def parseCommandArguments(cmdArgs):
    
    
   try:  
    parser = ThrowingArgumentParser()
    
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

        

# TODO: Sorry about this. It's a mess. Needs to be refactored.
#       Was done quickly.
def printHelp():
    print("\tSupported commands and syntax:")
    print("")
    
    print( NLFormat('search [-f <date>] [-u <date>] [-t <time step>] [-D] [-o <csv file>] [-n <number of tweets/period>] <query>', 72) )
    
    print('\tAbout:')
    print( NLFormat('     Performs a period search. Searches for tweets meeting conditions in <query> published between the dates specified in -f (from) and -u (until) arguments which is called a period. If -t , -u are missing, default date range is [two days ago - yesterday].  For a list of supported query operators see: https://developer.twitter.com/en/docs/twitter-api/v1/rules-and-filtering/search-operators . If -t option is specified then' +
                   ' the date range is divided into subranges according to the format specified by -t and search is conducted separately in each subrange. -n specifies how many' +
                   ' tweets to download during each subperiod. -o specifies the csv file to store tweets that meet the conditions. -D toggles the current debug mode on or off.'))
    print( NLFormat( "-f, -u: Datetimes should be enterred as Day/Month/YearTHour:Minutes:Seconds. Datetimes are always in UTC. Example: search -f 29/12/2021T10:07:55 -u 31/12/2021T08:32:11 euro crisis" ))
    print( NLFormat( "-t: Time steps should be specified in the following manner: kDmHnMzS where k, m, n and z integer values. Example 3D10H5M8S. -t format specifies how the date range specified " +
                    " by -f and -u arguments will be divided into subperiods, in each of which a seperate search will be conducted for the same query. For example the query search -f 3/2/2008 -u 10/2/2008 -t 2D10H5M2S euro " +
                    " will break up the date range [3/2/2008, 10/2/2008] to subperiods of length 2 days, 10 hours, 5 minutes and 2seconfs and conduct a search in each of these perids. In this example, search " +
                    "for the term euro in tweets will be conducted in the following periods separately:"))
    print( NLFormat('[ 03/02/2008 00:00:00 - 05/02/2008 10:05:02 ]'))
    print( NLFormat('[ 05/02/2008 10:05:02 - 07/02/2008 20:10:04 ]'))
    print( NLFormat('[ 07/02/2008 20:10:04 - 10/02/2008 00:00:00 ]'))
    print("")
    print( NLFormat('config') )
    print('\tAbout:')
    print( NLFormat('Displays currently loaded configuration settings.'))
    print("")
    print( NLFormat('reload [-c <path to configuration file>]') )
    print('\tAbout:')
    print( NLFormat('Allows loading a configuration file specified by the -c option. Relating file names are supported. In no -c option is provided, the config file loaded during startup is reloaded.'))                
    print('')
    print( NLFormat('history (alternatively h)' ) )
    print('\tAbout:')
    print( NLFormat('Displays the history of commands executed. Usefull to re-execute commands or copy-paste complicated commands'))
    print('')
    print( NLFormat('set target [historic | recent]' ) )
    print('\tAbout:')
    print( NLFormat('Specifies in which archive the search should be condicted. Value recent means that search is limited to tweets published the last 5 days. Value historic means that one may specify any time period without any constraint.' +
                    'Value recent and historic use different bearer tokens and hence tweets are accounted in different developer accounts. You get bearer tokens freely. recent bearer tokens are obtained by ' +
                    'simply opening a developer account. Search in the historic archive requires an academic bearer token that you can request.'))
    print('')
    print( NLFormat('!<index>' ) )
    print('\tAbout:')
    print( NLFormat('From the command history list (see history or h) executes the command at position <index>'))
    print('')
    print( NLFormat('!!' ) )
    print('\tAbout:')
    print( NLFormat('Re-executes last command.'))
    print('')
    print('')
    print( NLFormat('help' ) )
    print('\tAbout:')
    print( NLFormat('This screen.'))
    print('')
    print( NLFormat('quit or q' ) )
    print('\tAbout:')
    print( NLFormat('Terminates and quits the application.'))
    print('')


    print('')



  

         

def NLFormat(string, every=72):
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
commandShell = shellCommandExecutioner( configSettings )


# Simple command line interface to
# play around with Twitter API v2
#
#16/02/2022: Needs to be refactored. Is ugly. Have been
#            adding functionality quick and dirty. No extensive testing too. Sorry!  
while True:

  try:  
    command = input('[' + str(commandShell.commandsExecuted) + ']' + configSettings.get('General', 'commandPrompt', fallback="(default conf) >>> ") )
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


    
        
    if command.lower() not in ['history', 'h', 'quit', 'q']:           
           cHistory.addCommand( command )
    
    cParts = command.split()

    # NOTE: history/h command is the only command executed here!
    #       That's because the cHistory object is instantiated here
    # TODO: move it inside the shellCommandExecutioner class
    if cParts[0] == 'history' or   cParts[0] == 'h':
       cHistory.printHistory()
       continue


    # Execute command
    if commandShell.shellExecute( cParts ) :
       break
      
  except KeyboardInterrupt:
       print("\nKeyboard interrupt seen.")




  '''  
    #continue

    #
    # Let's check what command was given
    #
    if cParts[0].lower() == "search":
        continue
        qr = parseCommandArguments(cParts[1:])
        if qr is None:
          print("Usage: search [-f <from date>] [-u <to date>] [-n <number of tweets>] [-o <csv file>] [-D] <query>")
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
            configSettings['Debug']['debugMode'] =  str( not configSettings.getboolean('Debug', 'debugMode', fallback=False)) 



        # Perform actual search for tweets with the parameters given. 
        nFetched = tAPI.query( qr['from'], qr['until'], qr['timestep'], " ".join(qr['keywords']).strip() ) 
        if nFetched >= 0:
           print('Fetched total of', nFetched, 'tweets.')
        else:
           print('Error ', nFetched, 'encounterred.')   




        
        if configSettings.getboolean('Debug', 'debugMode', fallback=False):
           print('[DBUG] Setting debugMode back to [', oldVal, ']')

        # Restore old value    
        configSettings['Debug']['debugMode'] = oldVal
        
    
    elif cParts[0].lower() == "quit" or cParts[0].lower() == "q":
         break
    elif cParts[0].lower() == "config" or cParts[0].lower() == "settings":
         #displayConfigSettings(configSettings)
          pass
    elif cParts[0].lower() == "set":

         if cParts[1] == "target":
            setTargetArchive(configSettings, cParts[2])
         else:
             print('Unsupported parameter ', cParts[1])  

         continue             
         
    elif cParts[0].lower() == "helpAAA":
         printHelp() 
        
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
        print("OLD:::Unknown command:", cParts[0])
        print('Type help to see a list of commands.')

  except KeyboardInterrupt:
       print("\nKeyboard interrupt seen.")

  '''

       
cHistory.save()

print("\nFinished. ByeBye!")



