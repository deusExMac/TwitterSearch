import os
import csv
import datetime
import dateutil.parser
import configparser


#
# Class to save the tweets in various formats.
# The design tries to follow the Factory Method design pattern.
# See: https://realpython.com/factory-method-python/
#
#

class tweetWriterFactory:

    # TODO: complete me!
    def __init__(self):
        self._writers = {}
        
    def getWriter(self, writerFormat):
        if writerFormat.lower() == 'csv':
            return csvWriter()
        elif writerFormat.lower() == 'db':
            return dbWriter()
        else:
            return defaultWriter()
            #raise ValueError(writerFormat) # Unsupported format


# Default writer. Use this instead of raising exception
class defaultWriter:

      def write(self, tweetList=None, userList=None, cfg=None):
          count = 0
          for t in tweetList:
              count +=1
              print(str(count), '/', str(len(tweetList)), ') [', t['author_id'], ' ', t['id'], ' ', datetime.datetime.strptime(t['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y %H:%M:%S'), ']', sep='')
              
          return(count)


class csvWriter:

      def write(self, tweetList=None, userList=None, cfg=None):

        csvFile = None
          
        try:
            
          if not os.path.exists(cfg.get('Storage', 'csvFile', fallback="data.csv")):
             csvFile = open(cfg.get('Storage', 'csvFile', fallback="data.csv"), "w", newline="", encoding='utf-8')
             csvWriter = csv.writer(csvFile, delimiter=cfg.get('Storage', 'csvSeparator', fallback=',')) 
             csvWriter.writerow(['author_id', 'username', 'id', 'created_at(utc)', 'lang', 'tweet', 'likes', 'quotes', 'replies', 'retweets',  'tweetcount', 'followers', 'following', 'url'])
          else:      
             csvFile = open(cfg.get('Storage', 'csvFile', fallback="data.csv"), "a", newline="", encoding='utf-8')
             csvWriter = csv.writer(csvFile, delimiter=cfg.get('Storage', 'csvSeparator', fallback=',') ) 
             
          nWritten = 0          
          for t in tweetList:
              #author_id = t['author_id']
              author_id = t.get('author_id', '') #['author_id']

              # User metrics
              '''
              authorName = userList[author_id]['username']
              authorFollowers = userList[author_id]['public_metrics']['followers_count']
              authorFollowing = userList[author_id]['public_metrics']['following_count']
              authorTweetCount = userList[author_id]['public_metrics']['tweet_count']
              '''
              #print(author_id, ' Getting userList (', type(userList), ')')
              authorName = userList.get(author_id, {}).get('username', '')
              authorFollowers = userList.get(author_id, {}).get('public_metrics', {}).get('followers_count', '-1')
              authorFollowing = userList.get(author_id, {}).get('public_metrics', {}).get('following_count', '-1')
              authorTweetCount = userList.get(author_id, {}).get('public_metrics', {}).get('tweet_count', '-1')

              
              
              # Tweet metrics
              # TODO: Error checking! Make sure that this works even for very old tweets
              likeCount = t.get('public_metrics', {}).get('like_count', -1)
              quoteCount = t.get('public_metrics', {}).get('quote_count', -1)
              replyCount = t.get('public_metrics', {}).get('reply_count', -1)
              retweetCount = t.get('public_metrics', {}).get('retweet_count', -1)

              # Format date to be more readable. Dates are UTC 
              created_at = datetime.datetime.strptime(t['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y %H:%M:%S')
              
              tweet_id = t['id']
              lang = t['lang']
              text = t['text']
              text = text.replace('\r', ' ').replace('\n', ' ')
              text = text.replace( '\t', ' ' )
              text = text.replace( cfg.get('Storage', 'csvSeparator', fallback=','), " " )        
              text = text.replace( '"', ' ' )
              text = text.replace( "'", " " )

              url = 'https://twitter.com/twitter/status/' + tweet_id

              csvDataLine = [author_id, authorName, tweet_id, created_at, lang, text, likeCount, quoteCount, replyCount, retweetCount, authorTweetCount, authorFollowers, authorFollowing, url]
              csvWriter.writerow(csvDataLine)
              nWritten += 1
                        
          csvFile.close()
          return(nWritten)
        
        except Exception as fwEx:
               print( 'ERROR in writer:', str(fwEx) )
               if csvFile is not None:
                  csvFile.close()
                  
               return(-6)   
               
          


class dbWriter:

      def write(self, tweetList=None, userList=None, cfg=None):
          pass  
