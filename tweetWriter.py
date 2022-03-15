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
             csvWriter.writerow(['author id', 'created_at', 'id', 'lang', 'tweet', 'username', 'tweetcount', 'followers', 'following', 'url'])
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

              created_at = dateutil.parser.parse(t['created_at'])
              tweet_id = t['id']
              lang = t['lang']
              text = t['text']
              text = text.replace('\r', ' ').replace('\n', ' ')
              text = text.replace( '\t', ' ' )
              text = text.replace( cfg.get('Storage', 'csvSeparator', fallback=','), " " )        
              text = text.replace( '"', ' ' )
              text = text.replace( "'", " " )

              url = 'https://twitter.com/twitter/status/' + tweet_id

              csvDataLine = [author_id, created_at, tweet_id, lang, text, authorName, authorTweetCount, authorFollowers, authorFollowing, url]
              csvWriter.writerow(csvDataLine)
              nWritten += 1
              
          
          csvFile.close()
          return(nWritten)
          


class dbWriter:

      def write(self, tweetList=None, userList=None, cfg=None):
          pass  
