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
    # Fetch data for this period [sP - eP] only. 
    #
    def __qryPeriod(self, q, sP, eP):

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
             print('[ERROR] Code:',errCode, " Msg:[", errObj['title'], '] ', errObj['detail'])
             return(0-errCode) #make negative


          next_token, tweetsFetched, userRefs = self.__parseResponse( json_response )         
          #totalPeriodTweets += len(tweetsFetched)
          if totalPeriodTweets + len(tweetsFetched) >= self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ):
             # To test something
             # TODO: Fix this. Ugly.
             amount =  self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ) - totalPeriodTweets             
             nW = tWriter.write( tweetsFetched[0:amount], userRefs, self.configuration )
             
             totalPeriodTweets +=  amount
             print(".[Period total:",  totalPeriodTweets,']', sep='')
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )             
             return(totalPeriodTweets)


          if  len(tweetsFetched) > 0 :
              nW = tWriter.write( tweetsFetched, userRefs, self.configuration )
              totalPeriodTweets +=  len(tweetsFetched)
              if self.configuration.getboolean('Debug', 'showProgress', fallback=False):
                 print(".[pF:", len(tweetsFetched), ", pS:", len(tweetsFetched) , ", tpS:",totalPeriodTweets,']', sep='', end='' )
              else:
                  print('.', end='')
          
          # Next commented out code, not needed anymore

          '''
          if totalPeriodTweets >= self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ):
             print('Max tweets per period', self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ),' reached. Stopping')   
             return(totalPeriodTweets)
          '''
          
          if next_token is None:
             print('[DEBUG] >>>> Found  NONE next token')
             # Sleep but shorter. Just to make sure that consecutive requests do not bombard the server             
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )
             break
            
          #else:
          #   print('[DEBUG] Found valid next token')
          #   print('[DEBUG] Sleeping ', self.configuration.getfloat('Request', 'sleepTime', fallback=3.8))

          #print('Sleeping...')
          time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8) )          

        #print('Done (', totalPeriodTweets, ')')
        #print(".[", totalPeriodTweets,']' )  
        return(totalPeriodTweets)
            



    
    # Starting from here    
    def query(self, f, u, t, q):

        periods = self.createPeriods( f, u, t )
        if periods is None:
           print('Error creating periods.')
           return(-5)
        
        
        print("\nCommencing tweet search")
        print("Search parameters:")
        print("\tQuery:", q)
        print("\tTarget archive:", self.configuration.get('TwitterAPI', 'targetArchive', fallback="recent") )
        print("\tNumber of search periods:", len(periods))
        print("\tMaximum number of tweets to fetch in each period:",  self.configuration.get('General', 'maxTweetsPerPeriod', fallback="30"))
        print("\tNumber of tweets to ask from endpoint per request:",  self.configuration.getint('TwitterAPI', 'maxEndpointTweets', fallback=100) )
        print("\tTweets saved to csv file:",  self.configuration.get('Storage', 'csvFile', fallback="data.csv"), "\n" ) 

        time.sleep( 2.3 )

        totalTweets = 0
        for p in periods:
            print(">>> Period [", datetime.strptime(p['from'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S'), " - ", datetime.strptime(p['until'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S'), "] : Getting a maximum of [", self.configuration.get('General', 'maxTweetsPerPeriod', fallback='30' ),"] tweets for this period", sep="")
            nTweets = self.__qryPeriod(q, p['from'], p['until'])
            if nTweets < 0 :
               print('<<< Terminating due to error [', nTweets, ']') 
               return(nTweets)
            
            totalTweets += nTweets
            #print("\t>>>>", nTweets, 'for period')

        print('<<< Total of ', totalTweets, 'tweets downloaded')
        return( totalTweets )
        






    #
    # Generates periods based on steps specified by t
    # NOTE: from date f, until date u must be strings
    # formatted in ISO time (format %Y-%m-%dT%H:%M:%SZ).
    #
    def createPeriods(self, f, u, t ):

      tPeriods = []
    
      if datetime.strptime(f, "%Y-%m-%dT%H:%M:%SZ") > datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ"):
       print('Invalid dates: End-date [', u, '] must be after start-date [', f, ']') 
       return(None)
      
      if t == "":
       tPeriods.append( {'from': f, 'until': u} )
       if self.configuration.getboolean('Debug', 'debugMode', fallback=False):  
          print("\t[DEBUG] No time step specified. Adding SINGLE search period: [", datetime.strptime(f, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M:%S"), "-", datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M:%S"), "]")

       return(tPeriods)

      # Do some normalization if needed
      # TODO: DO we need this check????
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
           if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
              print("\t[DEBUG] Adding search period: [", sDate.strftime("%d/%m/%Y %H:%M:%S"), "-", eDate.strftime("%d/%m/%Y %H:%M:%S"), "]")
              
           return(tPeriods)
      
        if self.configuration.getboolean('Debug', 'debugMode', fallback=False):
           print("\t[DEBUG] Adding search period: [", sDate.strftime("%d/%m/%Y %H:%M:%S"), "-", eDate.strftime("%d/%m/%Y %H:%M:%S"), "]")
           
        tPeriods.append( {'from': sDate.strftime("%Y-%m-%dT%H:%M:%SZ"), 'until': eDate.strftime("%Y-%m-%dT%H:%M:%SZ")} )
        pCnt += 1
        sDate = sDate + timedelta(days= dayVal, hours = stepValue.hour, minutes = stepValue.minute, seconds=stepValue.second)

      # Remove this?
      return(tPeriods)




         

    def __parseResponse(self, jsn):
    
      
     resultCount = jsn['meta']['result_count']
     tweetsCollected = []
     userReferences = {}
     if resultCount is not None and resultCount > 0:
       #print("__parseResponse: Got ", resultCount, " tweets for this token")
    
              
       totalUsers = len(jsn['includes']['users'])
       for k in range(totalUsers):
           userReferences[jsn['includes']['users'][k]['id']] = jsn['includes']['users'][k]

       
       for tweet in jsn['data']:
           tweetsCollected.append( tweet )
           # currentTotalCount += 1           
           #if currentTotalCount >= self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ):
           #   return(None, nTokenCount) 
           
     if 'next_token' in jsn['meta']:
       # Save the token to use for next call
       nextToken = jsn['meta']['next_token']
     else:
          nextToken = None
     
     return( nextToken, tweetsCollected, userReferences )


    

    def __sendRequest(self, url, headers, params, next_token = None):
     params['next_token'] = next_token   
     response = requests.request("GET", url, headers = headers, params = params)
     if response.status_code != 200:
        #print('datatype:', type(response.text) )
        #print('>>>', response.text['detail'])
        #errObj = json.loads( response.text )
        #print('data type ==>', type(errObj) )
        raise Exception(response.status_code, response.text)
        return(None)
    
     return response.json()
