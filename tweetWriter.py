import os
import csv
import datetime
import dateutil.parser
import configparser


#
# Classe to save the tweets in various formats.
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
            raise ValueError(writerFormat)





class csvWriter:

      def write(self, tweetList=None, userList=None, cfg=None):

          if not os.path.exists(cfg.get('Storage', 'csvFile', fallback="data.csv")):
             csvFile = open(cfg.get('Storage', 'csvFile', fallback="data.csv"), "w", newline="", encoding='utf-8')
             csvWriter = csv.writer(csvFile, delimiter=cfg.get('Storage', 'csvSeparator', fallback=',')) 
             csvWriter.writerow(['author id', 'username', 'id', 'created_at(utc)', 'lang', 'tweet', 'tweetcount', 'followers', 'following', 'url'])
          else:      
             csvFile = open(cfg.get('Storage', 'csvFile', fallback="data.csv"), "a", newline="", encoding='utf-8')
             csvWriter = csv.writer(csvFile, delimiter=cfg.get('Storage', 'csvSeparator', fallback=',') ) 
             
          nWritten = 0          
          for t in tweetList:
              author_id = t['author_id']
              authorName = userList[author_id]['username']
              authorFollowers = userList[author_id]['public_metrics']['followers_count']
              authorFollowing = userList[author_id]['public_metrics']['following_count']
              authorTweetCount = userList[author_id]['public_metrics']['tweet_count']

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

              csvDataLine = [author_id, authorName, tweet_id, created_at, lang, text, authorTweetCount, authorFollowers, authorFollowing, url]
              csvWriter.writerow(csvDataLine)
              nWritten += 1
              
          
          csvFile.close()
          return(nWritten)
          


class dbWriter:

      def write(self, tweetList=None, userList=None, cfg=None):
          pass  
