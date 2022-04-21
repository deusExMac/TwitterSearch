



"""

Module containing class acting as wrapper for REST calls to the Twitter v2 API.

Author: mmt
Version: 20/04/2022

"""





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
        




    # TODO: do we need this?
    def isCustomExceptionMessage( ex ):
        if len(ex.args) < 2:
           return(False)        
        else:
           return(True)

        
        #         eC, eM = ex.args
        #         if eC == -69: #This was a keyboard interrupt.
        #            eObj = json.loads(eM)
        #            totalTweets += int(eObj["downloaded"])



    def buildRequest(self, q, sD, eD):
      try:  
        qParams = {'query': q,
                    'max_results': self.configuration.getint('TwitterAPI', 'maxEndpointTweets', fallback=100),
                    'expansions': self.configuration.get('TwitterAPI', 'expansions', fallback='author_id,in_reply_to_user_id,geo.place_id'),
                    'tweet.fields': self.configuration.get('TwitterAPI', 'tweet.fields', fallback='id,text'), #'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source'
                    'user.fields': self.configuration.get('TwitterAPI', 'user.fields', fallback='id,name'), #'id,name,username,created_at,description,public_metrics,verified'
                    'place.fields': self.configuration.get('TwitterAPI', 'place.fields', fallback='full_name,id,country,country_code,geo,name,place_type'), #'full_name,id,country,country_code,geo,name,place_type'
                    'next_token': {}}
        
        if sD =='' and  eD == '':
           # This is a simple search           
           bearerToken = self.configuration.get('TwitterAPI', 'essentialBearer', fallback='')
           if self.configuration.getboolean('TwitterAPI', 'bearerEncrypted', fallback=False):
              bearerToken = utils.kFileDecrypt(self.configuration.get('TwitterAPI', 'encryptionKeyFile', fallback='key'), bearerToken)

           rqH = {"Authorization": "Bearer {}".format( bearerToken )}
           rqSUrl = self.configuration.get('TwitterAPI', 'recentApiEndPoint', fallback="")
        else:
           # This is a period search
           bearerToken = self.configuration.get('TwitterAPI', 'Bearer', fallback='')
           if self.configuration.getboolean('TwitterAPI', 'bearerEncrypted', fallback=False):
              bearerToken = utils.kFileDecrypt(self.configuration.get('TwitterAPI', 'encryptionKeyFile', fallback='key'), bearerToken)
              
              
           rqH = {"Authorization": "Bearer {}".format( bearerToken )}
           rqSUrl = self.configuration.get('TwitterAPI', 'apiEndPoint', fallback="")
           # Add two more params: the dates
           qParams['start_time'] = sD
           qParams['end_time'] = eD

        return( rqSUrl, rqH, qParams )
    
      except Exception as bEx:
             #if self.isCustomExceptionMessage(bEx):
             raise bEx


         

    #
    # Do the actual query to the endpoint - used for simple and period queries.
    # ALso, uses the appriate writer to process the downloaded tweets.
    # 
    # TODO: This metho needs refactoring.It has become big and ugly.
    #       It has too many responsibilities.
    #
    def __qryGENERIC(self, q, sP, eP):
        

         ######################################
         # __qryGENERIC() method starts here
         ######################################

        from clrprint import clrprint as print

        #
        # TODO: redesign the code immediately following.
        #       e.g. add a method prepareParams(...) doing the job 
        
        next_token = None

        #
        # Prepare the query parameter.
        # Depending on the dates, we will do a simple or period query
        #

        try:  
           search_url, headers, query_params =  self.buildRequest( q, sP, eP )
        except Exception as qPEx:
               #print( str(qPEx) )
               if len(qPEx.args) < 2:                   
                  return(-3)
               else:
                    eC, eM = qPEx.args
                    eObj = json.loads(eM)
                    print("\n[ERROR]", eC, ':', eObj['message'])
                    return(eC)
               
            
                
        # Get an appropriate writer to save the tweets 
        tWriter = tweetWriter.tweetWriterFactory().getWriter( self.configuration.get('Storage', 'format', fallback='csv') )
        
             
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
             # TODO: better error handling. Exception might not be json. 
             errCode, errMsg = netEx.args
             errObj = json.loads(errMsg)             
             print('[ERROR] Code:',errCode, " Msg:[", errObj['title'], '] ', errObj['detail'] )
             return(errCode) 

          next_token, tweetsFetched, userRefs = self.__parseResponse( json_response )

          # Calculate download speed in tweets/sec
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
             print(utils.fL(".(" + str(len(tweetsFetched)) + "/" +  str(nW) + "/" + str(totalTweetsDownloaded) + ") [Total:" +  str(totalTweetsDownloaded) + '] at ' + "{:.2f}".format( statistics.mean(self.downloadSpeeds) ) + ' tweets/sec', prefix='   ', every=53), clr=random.choice(['r', 'g', 'b', 'y', 'p', 'm', 'd' ]), sep='' )
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
             
             print( utils.fL(".[Total:" +  str(totalTweetsDownloaded) +'] at ' + str("{:.2f}".format(statistics.mean(self.downloadSpeeds))) + ' tweets/sec', prefix='   ', every=53), clr=random.choice(['r', 'g', 'b', 'y', 'p', 'm', 'd' ]), sep='') 
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
               raise Exception(-69, '{"downloaded":"' + str(totalTweetsDownloaded)+'"}')
 
            
        return(totalTweetsDownloaded)
            
 


    ############################################


    # Fetches data (fields) for single Tweets.
    # idList: list with the ids of tweets to fetch.
    #
    
    def getTweets(self, idList, showErrors = False):

       bearerToken = self.configuration.get('TwitterAPI', 'Bearer', fallback='') 
       if self.configuration.getboolean('TwitterAPI', 'bearerEncrypted', fallback=False):
              bearerToken = utils.kFileDecrypt(self.configuration.get('TwitterAPI', 'encryptionKeyFile', fallback='key'), bearerToken)

       #print("[DEBUG bearer used:", bearerToken)       
       headers = {"Authorization": "Bearer {}".format( bearerToken )}
       query_params = {'ids': ','.join(idList),                    
                    'expansions': self.configuration.get('TwitterAPI', 'expansions', fallback='author_id,in_reply_to_user_id,geo.place_id'),
                    'tweet.fields': self.configuration.get('TwitterAPI', 'tweet.fields', fallback='id,text'), #'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source'
                    'user.fields': self.configuration.get('TwitterAPI', 'user.fields', fallback='id,name'), #'id,name,username,created_at,description,public_metrics,verified'
                    'place.fields': self.configuration.get('TwitterAPI', 'place.fields', fallback='full_name,id,country,country_code,geo,name,place_type'), #'full_name,id,country,country_code,geo,name,place_type'
                    'next_token': {}}

       try:
         json_response = self.__sendRequest('https://api.twitter.com/2/tweets', headers, query_params)
       except Exception as tEx:
           print( str(tEx) )
           return(None)

       nT, tweetsFetched, userRef, tErr = self.__parseResponse2(json_response)

       # Get a default writer
       tWriter = tweetWriter.tweetWriterFactory().getWriter( 'simple' )
       tWriter.write( tweetsFetched, userRef, self.configuration )

       if showErrors and len(tErr) > 0:
          print('\nTweet ids not fetched due to errors: ', end='')
          print( ','.join( tErr ) )
          print(' ' )
              
       return(0)
        




    
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
        print("\tTweets saved as format:",  self.configuration.get('Storage', 'format', fallback=""))
        print("\tTweets saved to csv file:",  self.configuration.get('Storage', 'csvFile', fallback="data.csv"))
        print("\tBearer encrypted:",  self.configuration.getboolean('TwitterAPI', 'bearerEncrypted', fallback=False))
        print("\tConfiguration file loaded:",  self.configuration.get('__Runtime', '__configsource', fallback="???"), "\n" ) 

        # sleep some short amount to allow user to see the settings.
        time.sleep( 2.3 )

        # Reset some variables to keep stats 
        avgPeriodTime = []  
        self.downloadSpeeds.clear() 
        totalTweets = 0
        pCount = 0
        print( utils.fL('', startOver=True), end='')
        for p in periods:
          try:  
            pCount += 1
            print(utils.fL( str(pCount) + '/' + str(len(periods)) +") Period [" + datetime.strptime(p['from'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S') + " - " + datetime.strptime(p['until'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S') + "] : Getting a maximum of [" + self.configuration.get('General', 'maxTweetsPerPeriod', fallback='30' ) + "] tweets for this period", startOver=True, every=68), clr='blue', end='')

            qStart = time.perf_counter()
            nTweets = self.__qryGENERIC(q, p['from'], p['until'])
            pElapsed = time.perf_counter() - qStart
            avgPeriodTime.append( pElapsed )
              
            if nTweets < 0 :
               return(nTweets)


            if self.configuration.getboolean('Debug', 'showProgress', fallback=False):               
               hms = str( timedelta(seconds= (len(periods) - pCount) * statistics.mean(avgPeriodTime)) ).split(':')
               #endTime = str( datetime.now() + timedelta(seconds= (len(periods) - pCount) * statistics.mean(avgPeriodTime)) )
               endTime = (datetime.now() + timedelta(seconds= (len(periods) - pCount) * statistics.mean(avgPeriodTime))).strftime('%d/%m/%Y %H:%M:%S')                
               print( utils.fL( '||[' + str(datetime.now()) + '] Done in ' + '{:.2f}'.format(pElapsed) + 's. Completion in: ' + hms[0] + ' hours, ' + hms[1] + ' minutes, ' + '{:.1f}'.format(float(hms[2])) + ' seconds (ETC: ' + endTime + ')', startOver=True, every=114 ), clr='green')
               
             
            print('')
            totalTweets += nTweets            
            # reset current line counter
            utils.clc = 0
          except Exception as ex:
              #print( str(ex) )
              if len(ex.args) < 2:
                 print('\n[ERROR]', ex.args[0], sep='') 
              else:    
                 eC, eM = ex.args
                 if eC == -69: #This was a keyboard interrupt.
                    eObj = json.loads(eM)
                    totalTweets += int(eObj["downloaded"])
              break   

        return( totalTweets )
        






    def simpleQuery(self, q):
        
        print("\nCommencing simple tweet search (no date constraints)")
        print("Search parameters:")
        print("\tQuery:", q)
        print("\tTarget archive: recent (forced)",  )
        print("\tNumber of search periods: 0")
        print("\tMaximum number of tweets to fetch:",  self.configuration.get('General', 'maxTweetsPerPeriod', fallback="30"))
        print("\tNumber of tweets to ask from endpoint per request:",  self.configuration.getint('TwitterAPI', 'maxEndpointTweets', fallback=100), ' (.)' )
        print("\tTweets saved as format:",  self.configuration.get('Storage', 'format', fallback=""))
        print("\tTweets saved to csv file:",  self.configuration.get('Storage', 'csvFile', fallback="data.csv"))
        print("\tBearer encrypted:",  self.configuration.getboolean('TwitterAPI', 'bearerEncrypted', fallback=False))
        print("\tConfiguration file loaded:",  self.configuration.get('__Runtime', '__configsource', fallback="???"), "\n" )

        # sleep some short amount to allow user to review the settings.
        time.sleep( 2.3 )

        self.downloadSpeeds.clear()
        try:
         nTweets = self.__qryGENERIC(q, '', '')
         return(nTweets)
        except Exception as qEx:            
          return(-7)







        

    def __parseResponse(self, jsn):
     
     try: 
       #resultCount = jsn['meta']['result_count']
       resultCount = jsn.get('meta', {}).get('result_count', 1) 
     except Exception as cEx:
       resultCount = 1 # We assume that it was a request for a single Tweet
       
     tweetsCollected = []
     userReferences = {}
     next_token = None
     
     if resultCount is not None and resultCount > 0:
       # Data about users are kept in different parts of the json
       # document. So, we extract this data and return it separately
       # from the list of tweets. 
       # totalUsers = len(jsn['includes']['users'])
       
       # TODO: Check if include is dict and users a list
       totalUsers = len(jsn.get('includes', {}).get('users', [])) #len(jsn['includes']['users'])
       for k in range(totalUsers):
           userReferences[jsn['includes']['users'][k]['id']] = jsn['includes']['users'][k]

       # Irerate and collect tweets now
       for tweet in jsn.get('data', {}): 
           tweetsCollected.append( tweet )
                      
     if 'next_token' in jsn.get('meta', {}):
       # Save the token to use for next call
       nextToken = jsn['meta']['next_token']
     else:
          nextToken = None

     
     return( nextToken, tweetsCollected, userReferences )







     #
     # Special form of parseResponse, used only
     # by getTweets.
     # As tweets with specified id
     # may not exist, this method returns also
     # tweet ids that resulted in errors (e.g.
     # could not be found).
     #
    def __parseResponse2(self, jsn):

         nT, tC, uR = self.__parseResponse(jsn)

         idE = []
         errs = jsn.get('errors', [])
         for e in errs:
             idE.append(e['resource_id'])

         return( nT, tC, uR, idE )     






    
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
