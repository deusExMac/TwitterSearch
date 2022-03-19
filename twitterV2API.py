import datetime
import dateutil.parser
from datetime import datetime, timedelta
import requests
import configparser
import time
import json

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
         
         
            
    def __init__(self, cfg):
        self.configuration = cfg
        


    def setConfiguration(self, cfg):
        self.configuration = cfg
        



    #
    # Fetch data for this period [sP - eP] ONLY. 
    #
    def __qryPeriod(self, q, sP, eP):

        # inline/nested function
        # TODO: use this here
        def NLFormat(string, every=72):
            lines = []
            for i in range(0, len(string), every):
                lines.append('\t' + string[i:i+every])

            return '\n'.join(lines)

         ######################################
         # __qryPeriod() method starts here
         ######################################
        
        next_token = None
        headers = {"Authorization": "Bearer {}".format( self.configuration.get('TwitterAPI', 'Bearer', fallback='') )}
        search_url = self.configuration.get('TwitterAPI', 'apiEndPoint', fallback="")
        
        # TODO: move this out of here as it will be called many times? i.e. This is executed FOR EVERY PERIOD!
        try:
            # Get an appropriate writer to save the tweets 
            tWriter = tweetWriter.tweetWriterFactory().getWriter( self.configuration.get('Storage', 'format', fallback='csv') )
        except Exception as fEx:
            print('Error initializing writer. Unknown format [', self.configuration.get('Storage', 'format', fallback='csv'), ']')
            return(-7)
             
        
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

        
        numRequests = 0
        totalPeriodTweets = 0
        while True:
            
          try:
            json_response = self.__sendRequest(search_url, headers, query_params, next_token)
            numRequests += 1
          except Exception as netEx:
             errCode, errMsg = netEx.args
             errObj = json.loads(errMsg)             
             print('[ERROR] Code:',errCode, " Msg:[", errObj['title'], '] ', errObj['detail'] )
             return(errCode) 


          next_token, tweetsFetched, userRefs = self.__parseResponse( json_response )         

          if self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) > 0:
              
           if totalPeriodTweets + len(tweetsFetched) >= self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ):

             if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
                print('[DEBUG] Reached period tweet limit of', self.configuration.get('General', 'maxTweetsPerPeriod', fallback='30' ),'. Terminating period search')
                print('[DEBUG] Last batch:', self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) - totalPeriodTweets, ' tweets')
                
             # To test something
             # TODO: Fix this. Ugly.
             amount =  self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) - totalPeriodTweets             
             nW = tWriter.write( tweetsFetched[0:amount], userRefs, self.configuration )
             if nW < 0 :
                return(nW)
            
             totalPeriodTweets +=  amount
             print(".[Period total:",  totalPeriodTweets,']', sep='')
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )             
             return(totalPeriodTweets)



          if  len(tweetsFetched) > 0 :
              nW = tWriter.write( tweetsFetched, userRefs, self.configuration )
              if nW < 0:
                 return(nW) 
              totalPeriodTweets +=  nW
              if self.configuration.getboolean('Debug', 'showProgress', fallback=False) or self.configuration.getboolean('Debug', 'debugMode', fallback=False):
                 print(". (prF:", len(tweetsFetched), ", prS:", nW , ", ptS:",totalPeriodTweets,')', sep='', end='' )
              else:
                  print('.', end='')
          
          
          
          if next_token is None:
             print("[Period total:",  totalPeriodTweets,']') 
             if self.configuration.getboolean('Debug', 'debugMode', fallback=False): 
                print('[DEBUG] >>>> Found  NONE next token. Terminating period search.')
                
             # Sleep but shorter. Just to make sure that consecutive requests do not bombard the server             
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )
             break
            
          #else:
          #   print('[DEBUG] Found valid next token')
          #   print('[DEBUG] Sleeping ', self.configuration.getfloat('Request', 'sleepTime', fallback=3.8))

          #print('Sleeping...')
          if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
             print('[DEBUG] Sleeping for [', self.configuration.getfloat('Request', 'sleepTime', fallback=3.8), '] seconds')
             
          time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8) )          


        #print('Done (', totalPeriodTweets, ')')
        #print(".[", totalPeriodTweets,']' )  
        return(totalPeriodTweets)
            



    
    # Does a search for tweets on specific dates (periods).
    # If no date range is provided, one is generated
    # automatically as the last 3 days.
    def periodQuery(self, f, u, t, q):


        if q.strip() == '':
           print('Empty query')
           return(-1)

        if f.strip() == '' or u.strip() == '':
           print('Invalid dates')
           return(-2)
        
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

        totalTweets = 0
        for p in periods:
            print(">>> Period [", datetime.strptime(p['from'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S'), " - ", datetime.strptime(p['until'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S'), "] : Getting a maximum of [", self.configuration.get('General', 'maxTweetsPerPeriod', fallback='30' ),"] tweets for this period", sep="")
            nTweets = self.__qryPeriod(q, p['from'], p['until'])
            if nTweets < 0 :
               #print('<<< Terminating due to error [', nTweets, ']') 
               return(nTweets)
            
            totalTweets += nTweets
            

        #print('<<< Total of ', totalTweets, 'tweets downloaded')
        return( totalTweets )
        





    #
    # Search for data. No date periods. Will search only in recent archive 
    # TODO: Integrate and combine this with __qryPeriod method
    #
    def __qry(self, q):

        # inline/nested function
        # TODO: use this here
        def NLFormat(string, every=72):
            lines = []
            for i in range(0, len(string), every):
                lines.append('\t' + string[i:i+every])

            return '\n'.join(lines)


         ######################################
         # __qry() method starts here
         ######################################

        
        next_token = None

        # We take directly the Bearer tokens and Urls for the recent archive. A simple search is always conducted on the
        # recent archive.
        # We do this in order not to overload bearer tokens.
        headers = {"Authorization": "Bearer {}".format( self.configuration.get('TwitterAPI', 'essentialBearer', fallback='') )}
        search_url = self.configuration.get('TwitterAPI', 'recentApiEndPoint', fallback="")

        if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
           print('[DEBUG] Bearer set to: [', self.configuration.get('TwitterAPI', 'essentialBearer', fallback='') , ']', sep='')
           print('[DEBUG] Search url set to: [', search_url , ']', sep='') 
        
        # TODO: move this out of here as it will be called many times? i.e. This is executed FOR EVERY PERIOD!
        try:
            # Get an appropriate writer to save the tweets 
            tWriter = tweetWriter.tweetWriterFactory().getWriter( self.configuration.get('Storage', 'format', fallback='csv') )
        except Exception as fEx:
            print('Error initializing writer. Unknown format [', self.configuration.get('Storage', 'format', fallback='csv'), ']')
            return(-7)
             
        
        # TODO: make this a instance var???
        query_params = {'query': q,
                    'max_results': self.configuration.getint('TwitterAPI', 'maxEndpointTweets', fallback=100),
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}

        
        numRequests = 0
        totalPeriodTweets = 0
        while True:
            
          try:
            json_response = self.__sendRequest(search_url, headers, query_params, next_token)
            numRequests += 1
          except Exception as netEx:
             errCode, errMsg = netEx.args
             errObj = json.loads(errMsg)
             print('[ERROR] Code:',errCode, " Msg:[", errObj['title'], '] ', errObj['detail'], ' Message:', errObj['errors'][0]['message'] )
             return(errCode) 


          next_token, tweetsFetched, userRefs = self.__parseResponse( json_response )         

          if self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) > 0:
              
           if totalPeriodTweets + len(tweetsFetched) >= self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ):

             if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
                print('[DEBUG] Reached period tweet limit of', self.configuration.get('General', 'maxTweetsPerPeriod', fallback='30' ),'. Terminating period search')
                print('[DEBUG] Last batch:', self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) - totalPeriodTweets, ' tweets')
                
             # To test something
             # TODO: Fix this. Ugly.
             amount =  self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) - totalPeriodTweets             
             nW = tWriter.write( tweetsFetched[0:amount], userRefs, self.configuration )
             if nW < 0 :
                return(nW)
            
             totalPeriodTweets +=  amount
             print(".[Period total:",  totalPeriodTweets,']', sep='')
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )             
             return(totalPeriodTweets)



          if  len(tweetsFetched) > 0 :
              nW = tWriter.write( tweetsFetched, userRefs, self.configuration )
              if nW < 0:
                 return(nW) 
              totalPeriodTweets +=  nW
              if self.configuration.getboolean('Debug', 'showProgress', fallback=False) or self.configuration.getboolean('Debug', 'debugMode', fallback=False):
                 print(". (prF:", len(tweetsFetched), ", prS:", nW , ", ptS:",totalPeriodTweets,')', sep='', end='' )
              else:
                  print('.', end='')
          
          
          
          if next_token is None:
             print("[Period total:",  totalPeriodTweets,']') 
             if self.configuration.getboolean('Debug', 'debugMode', fallback=False): 
                print('[DEBUG] >>>> Found  NONE next token. Terminating period search.')
                
             # Sleep but shorter. Just to make sure that consecutive requests do not bombard the server             
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )
             break
            
          
          if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
             print('[DEBUG] Sleeping for [', self.configuration.getfloat('Request', 'sleepTime', fallback=3.8), '] seconds')
             
          time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8) )          


        return(totalPeriodTweets)
  




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
        
        return( self.__qry(q) )






        

    def __parseResponse(self, jsn):
    
      
     resultCount = jsn['meta']['result_count']
     tweetsCollected = []
     userReferences = {}
     next_token = None
     if resultCount is not None and resultCount > 0:
              
       totalUsers = len(jsn['includes']['users'])
       for k in range(totalUsers):
           userReferences[jsn['includes']['users'][k]['id']] = jsn['includes']['users'][k]

       
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
       response = requests.request("GET", url, headers = headers, params = params)
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
