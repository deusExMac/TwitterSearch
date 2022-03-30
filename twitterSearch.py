# How to use Twitter's v2 API to searcha nd download for tweets.
# IMPORTANT! In order to properly execute this program, you'll need
#            to create a Twitter developer account and get an access and bearer token.
#
# The developed was dased on the source code found here:
#    https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
#
# TODO: This has been created in a hurry. Needs serious refactoring.
#
# v0.82b mmtrd30/03/2022
# v0.77b mmtrd18/03/2022
# v0.4b mmtrd31/12/2021





import os
import os.path
import sys

import configparser
import argparse


# We define constants in this file
import appConstants
import commandShell






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




'''
def log(logF, m):
    with open(logF, 'a') as lF:
         lF.write('[' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '] ' + m + '\n')
'''


def generateDefaultConfiguration():
    cS = configparser.RawConfigParser(allow_no_value=True)
    cS.add_section('General')
    cS.add_section('Network')
    cS.add_section('TwitterAPI')
    cS.add_section('Request')
    cS.add_section('Storage')
    cS.add_section('Shell')
    cS.add_section('Debug')
    return(cS)
    


def setTargetArchive(cfg, md):
    if md.lower() == "recent":
       if 'TwitterAPI' in cfg.sections():
           cfg.set('TwitterAPI', 'apiEndPoint', cfg.get('TwitterAPI', 'recentApiEndPoint', fallback='XXXXX') )
           #cfg['TwitterAPI']['apiEndPoint'] =  cfg['TwitterAPI']['recentApiEndPoint']

           cfg.set('TwitterAPI', 'bearer', cfg.get('TwitterAPI', 'essentialBearer', fallback='YYYYYY') )
           #cfg['TwitterAPI']['bearer'] =  cfg['TwitterAPI']['essentialBearer']

           cfg.set('TwitterAPI', 'targetArchive', 'recent')
           #cfg['TwitterAPI']['targetArchive'] = 'recent'
           print("\tTarget archive set to recent.")
           return(0)
    elif  md.lower() == "historic":
          cfg.set('TwitterAPI', 'apiEndPoint', cfg.get('TwitterAPI', 'historicApiEndPoint', fallback='ZZZZZZ') )
          #cfg['TwitterAPI']['apiEndPoint'] =  cfg['TwitterAPI']['historicApiEndPoint']

          cfg.set('TwitterAPI', 'bearer', cfg.get('TwitterAPI', 'academicBearer', fallback='AAAAAA') )
          #cfg['TwitterAPI']['bearer'] =  cfg['TwitterAPI']['academicBearer']

          cfg.set('TwitterAPI', 'targetArchive', 'historic' )
          #cfg['TwitterAPI']['targetArchive'] = 'historic'
          print("\tTarget archive set to historic.")
          return(0)
    else:
          print("\tInvalid target archive option [", md, "] in configuration file. Use historic or recent.", sep='')
          return(-4)

        


  

         


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

print('')
print('Python v', sys.version)
print("")      
        
print('TwitterSearch v'+appConstants.APPVERSION, 'rd', appConstants.VERSIONRELEASEDATE )

# Note: We use .RawConfigParser() because some configuration strings contain special chars like % that
#       have special meaning for the ConfigParser class
configSettings = configparser.RawConfigParser(allow_no_value=True)

 
print('\tLoading configuration file [', configFile, ']........', sep='', end='')
# Load config file
if not os.path.exists(configFile):
   print("ERROR. File not found. Continuing with default settings.", sep="")
   configSettings = generateDefaultConfiguration()
   
else:
   try:        
    configSettings.read(configFile)
    configSettings.add_section('__Runtime')
    configSettings['__Runtime']['__configSource'] = configFile  
    print('OK', sep="")
   except Exception as cfgEx:    
      print('Error reading file [', configFile, ']. Continuing with default settings.', sep="")
      print(str(cfgEx))
      configSettings = generateDefaultConfiguration()
      #sys.exit()
    



# Set the target archive, that will set the Bearer token properly
sts = setTargetArchive(configSettings, configSettings.get('TwitterAPI', 'targetArchive', fallback="recent") )
if sts != 0:
   print('Fatal error. Terminating.')
   sys.exit()

print("\nType 'help' to see a list of supported commands.\n")

appShell = commandShell.commandShell( configSettings )
appShell.startShell()


print("\nFinished. ByeBye!")


