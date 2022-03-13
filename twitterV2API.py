import datetime
import dateutil.parser
from datetime import datetime, timedelta
import requests
import configparser
import time

import configparser
import appConstants

class twitterSearchClient:

    def __init__(self):
         self.configuration = configparser.RawConfigParser(allow_no_value=True)
         self.configuration.read(appConstants.DEFAULTCONFIGFILE)
         self.configuration.add_section('__Runtime')
         self.configuration['__Runtime']['__configSource'] = appConstants.DEFAULTCONFIGFILE
         
            
    def __init__(self, cfg):
        self.configuration = cfg
        #self.previousRequestTime = None
        


    def setConfiguration(self, cfg):
        self.configuration = cfg
        #print(self.configuration)



    #
    # Fetch data for this period [sP - eP] only. 
    #
    def __qryPeriod(self, q, sP, eP):

        next_token = None
        headers = {"Authorization": "Bearer {}".format( self.configuration.get('TwitterAPI', 'Bearer', fallback='') )}
        search_url = self.configuration.get('TwitterAPI', 'apiEndPoint', fallback="")

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
             print( str(netEx) )
             return(None)

          next_token, tweetCount = self.__parseResponse( json_response, totalPeriodTweets )         
          totalPeriodTweets += tweetCount
          print(".[TknC:", tweetCount, ", TotalC:",totalPeriodTweets,']', sep='', end='' )
          '''
          if totalPeriodTweets >= self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ):
             print('Max tweets per period', self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ),' reached. Stopping')   
             return(totalPeriodTweets)
          '''  
          if next_token is None:
             #print('[DEBUG] >>>> Found  NONE next token')
             # Sleep but shorter. Just to make sure that consecutive requests do not bombard the server
             
             time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8)/2.0 )
             break
            
          #else:
          #   print('[DEBUG] Found valid next token')
          #   print('[DEBUG] Sleeping ', self.configuration.getfloat('Request', 'sleepTime', fallback=3.8))

          #print('Sleeping...')
          time.sleep( self.configuration.getfloat('Request', 'sleepTime', fallback=3.8) )

        #print('Done (', totalPeriodTweets, ')')
        print(".[", totalPeriodTweets,']' )  
        return(totalPeriodTweets)
            



    
    # Starting from here    
    def query(self, f, u, t, q):

        periods = self.createPeriods( f, u, t )
        if periods is None:
           print('Error creating periods.')
           return(None)
        
        for p in periods:
            print(">>> Period [", datetime.strptime(p['from'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S'), " - ", datetime.strptime(p['until'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M:%S'), "] : Getting a maximum of [", self.configuration.get('General', 'maxTweetsPerPeriod', fallback='30' ),"] tweets for this period", sep="")
            nTweets = self.__qryPeriod(q, p['from'], p['until'])
            print("\t>>>>", nTweets, 'for period')
      
        






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




         

    def __parseResponse(self, jsn, currentTotalCount):
    
     resultCount = jsn['meta']['result_count']
    
     if resultCount is not None and resultCount > 0:
       #print("__parseResponse: Got ", resultCount, " tweets for this token")
    
       nTokenCount = 0 # how many tweets from this token were extracted
       for tweet in jsn['data']:
           currentTotalCount += 1
           nTokenCount += 1
           if currentTotalCount >= self.configuration.getint('General', 'maxTweetsPerPeriod', fallback=30 ):
              return(None, nTokenCount) 
           
     if 'next_token' in jsn['meta']:
       # Save the token to use for next call
       nextToken = jsn['meta']['next_token']
     else:
          nextToken = None
     
     return( nextToken, resultCount )
    

    def __sendRequest(self, url, headers, params, next_token = None):
     params['next_token'] = next_token   
     response = requests.request("GET", url, headers = headers, params = params)
     if response.status_code != 200:
        raise Exception(response.status_code, response.text)
        return(None)
    
     return response.json()
