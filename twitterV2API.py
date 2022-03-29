import datetime
import dateutil.parser
from datetime import datetime, timedelta
import requests
import time
import json
import statistics
import random

import configparser
import appConstants
import tweetWriter
import utils


class twitterSearchClient:

    def __init__(self):
         self.configuration = configparser.RawConfigParser(allow_no_value=True)
         self.configuration.read(appConstants.DEFAULTCONFIGFILE)
         self.configuration.add_section('__Runtime')
         self.configuration['__Runtime']['__configSource'] = appConstants.DEFAULTCONFIGFILE
         self.downloadSpeeds = [] 
         
            
    def __init__(self, cfg):
        self.configuration = cfg
        self.downloadSpeeds = [] 
        


    def setConfiguration(self, cfg):
        self.configuration = cfg
        

    
        

    #
    # Do the actual query to the endpoint - used for simple and period queries. 
    # TODO: Refactor this method. It's ugly
    #
    def __qryGENERIC(self, q, sP, eP):
        

         ######################################
         # __qryGENERIC() method starts here
         ######################################

        from clrprint import clrprint as print

        #
        # TODO: redesign the code immediately following
        #
        
        next_token = None

        #
        # Depending on the dates, we will do a simple or period query
        #
        
        if sP =='' and  eP == '':
           headers = {"Authorization": "Bearer {}".format( self.configuration.get('TwitterAPI', 'essentialBearer', fallback='') )}
           search_url = self.configuration.get('TwitterAPI', 'recentApiEndPoint', fallback="")
           query_params = {'query': q,
                    'max_results': self.configuration.getint('TwitterAPI', 'maxEndpointTweets', fallback=100),
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
        else:
           headers = {"Authorization": "Bearer {}".format( self.configuration.get('TwitterAPI', 'Bearer', fallback='') )}
           search_url = self.configuration.get('TwitterAPI', 'apiEndPoint', fallback="")
           # TODO: make this a instance var???        
           query_params = {'query': q,
                    'start_time': sP,
                    'end_time': eP,
                    'max_results': self.configuration.getint('TwitterAPI', 'maxEndpointTweets', fallback=100),
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
         
      
        
        # TODO: move this out of here as it will be called many times? i.e. This is executed FOR EVERY PERIOD!
        try:
            # Get an appropriate writer to save the tweets 
            tWriter = tweetWriter.tweetWriterFactory().getWriter( self.configuration.get('Storage', 'format', fallback='csv') )
        except Exception as fEx:
            print('Error initializing writer. Unknown format [', self.configuration.get('Storage', 'format', fallback='csv'), ']')
            return(-7)
             
        numRequests = 0
        totalTweetsDownloaded = 0
        print( utils.fL('', startOver=True), end='')
        
        try:        
         while True:
            
          try:
            # Start counting time in order to calculate speed
            tic = time.perf_counter()  
            json_response = self.__sendRequest(search_url, headers, query_params, next_token)
            numRequests += 1
          except Exception as netEx:
             errCode, errMsg = netEx.args
             errObj = json.loads(errMsg)             
             print('[ERROR] Code:',errCode, " Msg:[", errObj['title'], '] ', errObj['detail'] )
             return(errCode) 

          next_token, tweetsFetched, userRefs = self.__parseResponse( json_response )
          
          dSpeed = len(tweetsFetched)/(time.perf_counter() - tic)
          if len(self.downloadSpeeds) >= self.configuration.getint('General', 'downloadSpeedWindow', fallback=100 ):
             self.downloadSpeeds.pop(0) # if list is full, remove oldest one to add another one
             
          self.downloadSpeeds.append( dSpeed )
          
          if self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) > 0:
              
           if totalTweetsDownloaded + len(tweetsFetched) >= self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ):

             if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
                print('[DEBUG] Reached period tweet limit of', self.configuration.get('General', 'maxTweetsPerPeriod', fallback='30' ),'. Terminating period search')
                print('[DEBUG] Last batch:', self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) - totalTweetsDownloaded, ' tweets')
                
             # To test something
             # TODO: Fix this. Ugly.
             amount =  self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) - totalTweetsDownloaded             
             nW = tWriter.write( tweetsFetched[0:amount], userRefs, self.configuration )
             if nW < 0 :
                return(nW)
            
             totalTweetsDownloaded +=  amount
             print(utils.fL(".[Total:" +  str(totalTweetsDownloaded) + '] at ' + "{:.2f}".format( statistics.mean(self.downloadSpeeds) ) + ' tweets/sec', prefix='   ', every=53), clr=random.choice(['r', 'g', 'b', 'y', 'p', 'm', 'd' ]), sep='' )
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )             
             return(totalTweetsDownloaded)



          if  len(tweetsFetched) > 0 :
              nW = tWriter.write( tweetsFetched, userRefs, self.configuration )
              if nW < 0:
                 return(nW)
                
              totalTweetsDownloaded +=  nW
              if self.configuration.getboolean('Debug', 'showProgress', fallback=False) or self.configuration.getboolean('Debug', 'debugMode', fallback=False):
                 print( utils.fL(".(" + str(len(tweetsFetched)) + "/" +  str(nW) + "/" + str(totalTweetsDownloaded) + '/' + str("{:.2f}".format( statistics.mean(self.downloadSpeeds) )) + ')', prefix='   ', every=53), clr=random.choice(['r', 'g', 'b', 'y', 'p', 'm', 'd' ]), sep='', end='')                 
              else:
                  print(utils.fL('.', prefix='   ', every=53), clr=random.choice(['r', 'g', 'b', 'y', 'p', 'm', 'd' ]), end='')
                    
          
          if next_token is None:
             
             print( utils.fL(".[Total:" +  str(totalTweetsDownloaded) +'] at ' + str("{:.2f}".format(statistics.mean(self.downloadSpeeds))) + ' tweets/sec'), clr=random.choice(['r', 'g', 'b', 'y', 'p', 'm', 'd' ]), sep='') 
             if self.configuration.getboolean('Debug', 'debugMode', fallback=False): 
                print('[DEBUG] >>>> Found  NONE next token. Terminating period search.')
                
             # Sleep but shorter. Just to make sure that consecutive requests do not bombard the server             
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )
             break
            
         
          if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
             print('[DEBUG] Sleeping for [', self.configuration.getfloat('Request', 'sleepTime', fallback=3.8), '] seconds')

          
          time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8) )          

        except KeyboardInterrupt:        
               print('\nKeyboard interrupt seen. Stopping querying for tweets...')
 
            
        return(totalTweetsDownloaded)
            
 


    ############################################




    
    # Does a search for tweets on specific dates (periods).
    # If no date range is provided, one is generated
    # automatically as the last 3 days.
    def periodQuery(self, f, u, t, q):

        from clrprint import clrprint as print
        
        if q.strip() == '':
           print('Empty query')
           return(-1)

        if f.strip() == '' or u.strip() == '':
           print('Invalid dates')
           return(-2)

        # Chop up date f-u in junks of length specified by t.
        # If t is empty, add just one period.
        periods = utils.generateSubperiods( f, u, t, self.configuration )
        if periods is None:
           print('Error creating periods.')
           return(-5)
        
        
        print("\nCommencing tweet search")
        print("Search parameters:")
        print("\tQuery:", q)
        print("\tTarget archive:", self.configuration.get('TwitterAPI', 'targetArchive', fallback="recent") )
        print("\tNumber of search periods:", len(periods))
        print("\tMaximum number of tweets to fetch in each period:",  self.configuration.get('General', 'maxTweetsPerPeriod', fallback="30"))
        print("\tNumber of tweets to ask from endpoint per request:",  self.configuration.getint('TwitterAPI', 'maxEndpointTweets', fallback=100), ' (.)' )
        print("\tTweets saved to csv file:",  self.configuration.get('Storage', 'csvFile', fallback="data.csv"))
        print("\tConfiguration file loaded:",  self.configuration.get('__Runtime', '__configsource', fallback="???"), "\n" ) 

        # sleep some short amount to allow user to see the settings.
        time.sleep( 2.3 )

        self.downloadSpeeds.clear() 
        totalTweets = 0
        pCount = 0
        print( utils.fL('', startOver=True), end='')
        for p in periods:
            pCount += 1
            print(utils.fL( str(pCount) + '/' + str(len(periods)) +") Period [" + datetime.strptime(p['from'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S') + " - " + datetime.strptime(p['until'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S') + "] : Getting a maximum of [" + self.configuration.get('General', 'maxTweetsPerPeriod', fallback='30' ) + "] tweets for this period", startOver=True, every=68), clr='blue', end='')             
            nTweets = self.__qryGENERIC(q, p['from'], p['until'])
            if nTweets < 0 :
               return(nTweets)

            print('')
            totalTweets += nTweets
            utils.currentLineChars = 0 # Do we need this???
            utils.clc = 0
            

        return( totalTweets )
        








    def simpleQuery(self, q):
        
        print("\nCommencing simple tweet search (no date constraints)")
        print("Search parameters:")
        print("\tQuery:", q)
        print("\tTarget archive: recent (forced)",  )
        print("\tNumber of search periods: 0")
        print("\tMaximum number of tweets to fetch:",  self.configuration.get('General', 'maxTweetsPerPeriod', fallback="30"))
        print("\tNumber of tweets to ask from endpoint per request:",  self.configuration.getint('TwitterAPI', 'maxEndpointTweets', fallback=100), ' (.)' )
        print("\tTweets saved to csv file:",  self.configuration.get('Storage', 'csvFile', fallback="data.csv"))
        print("\tConfiguration file loaded:",  self.configuration.get('__Runtime', '__configsource', fallback="???"), "\n" )

        # sleep some short amount to allow user to review the settings.
        time.sleep( 2.3 )

        self.downloadSpeeds.clear()
        return( self.__qryGENERIC(q, '', '') )






        

    def __parseResponse(self, jsn):
    
      
     resultCount = jsn['meta']['result_count']
     tweetsCollected = []
     userReferences = {}
     next_token = None
     
     if resultCount is not None and resultCount > 0:
       # Data about users are kept in different parts of the json
       # document. So, we extract this data and return it separately
       # from the list of tweets. 
       totalUsers = len(jsn['includes']['users'])
       for k in range(totalUsers):
           userReferences[jsn['includes']['users'][k]['id']] = jsn['includes']['users'][k]

       # Irerate and collect tweets now
       for tweet in jsn['data']:
           tweetsCollected.append( tweet )
                      
     if 'next_token' in jsn['meta']:
       # Save the token to use for next call
       nextToken = jsn['meta']['next_token']
     else:
          nextToken = None

     
     return( nextToken, tweetsCollected, userReferences )


    
    #
    # TODO: Needs refactoring
    # 
    def __sendRequest(self, url, headers, params, next_token = None):
        
     params['next_token'] = next_token
     try:
       cTm = self.configuration.getfloat('Network', 'netConnectTimeout', fallback=-1)
       if cTm <= 0 :          
          cTm = None
       

       rTm = self.configuration.getfloat('Network', 'netReadTimeout', fallback=-1)
       if rTm <= 0:          
          rTm = None
          
       response = requests.request("GET", url, headers = headers, params = params, timeout=(cTm, rTm)  )
       
     except Exception as netEx:
         if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
            print('[DEBUG] Network error.')
            
         raise Exception(-8, '{"title":"Network error", "detail":"'+str(netEx) + '"}')
         
        
     if response.status_code != 200:
        if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
            print('[DEBUG] Response error [', response.text, ']')           
        # make errors negative
        raise Exception(0-response.status_code, response.text)
        

     # No error. Return response as json object
     return response.json()
