# For saving access tokens and for file management when creating and adding to the dataset
import os
import os.path

import configparser

# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
from datetime import datetime, timedelta



import argparse
import copy

import pandas as pd


# We define constants in this file
import appConstants
from commandHistory import commandHistory
import twitterV2API 
import utils



# The following two classes are used to parse
# arguments on the shell 'scommand line
class ArgumentParserError(Exception): pass
  
class ThrowingArgumentParser(argparse.ArgumentParser):
      def error(self, message):
          raise ArgumentParserError(message)






class commandShell:

      def __init__(self, cfg):

          # add here any command you would like to expand
          self.cmdExpansions = [{"c":"config"} ]
          
          self.cmdExecutioner = shellCommandExecutioner(cfg)
          self.cmdHistory = commandHistory(cfg.getint('Shell', 'historySize', fallback=10), True)





      #
      # Check if the command given needs to be expanded
      #
      def expandCommand( self, cmd ):

          # Is it in our manual expansion list?
          for c in self.cmdExpansions:
            if c.get(cmd) is not None:
               return( c.get(cmd) )

            
                
          if cmd == '!!':
             return( self.cmdHistory.getLast() )
                  
          if cmd.startswith('!'):
             try:
               hIdx = int(cmd[1:])
               return( self.cmdHistory.get(hIdx) )
               
             except Exception as nmbrEx:
                 #print('Executing last command starting with [', command[1:], ']', sep='')
                 return( self.cmdHistory.getLastStartingWith(cmd[1:] ) )
                   
          if cmd.startswith('^'):
             tokens = cmd.split('^')
             lcmd = self.cmdHistory.getLast()
             if lcmd == '':
                return('')
            
             #print('>>>', cmd.replace(tokens[1], tokens[2]))
             if len(tokens) < 3:
                return('')
            
             return( lcmd.replace(tokens[1], tokens[2]) )

          return(cmd)  


      def displayCommandHistory(self, n, fromBegin=False):
          
          if n > len(self.cmdHistory.commandHistory):
             n = len(self.cmdHistory.commandHistory)
          elif n <= 0:
               return
                               
          cList = self.cmdHistory.getN(n, fromBegin)
          #  counting commands
          if fromBegin:
             pos = 1
          else:   
             pos = len(self.cmdHistory.commandHistory)  - n + 1
             
          for c in cList:
              print(pos, '. ', c, sep='')
              pos += 1

                     



      def startShell(self):

                    
          while True:
                
             try:
                   
              command = input('(v' + appConstants.APPVERSION + ')' +'{' + str(self.cmdExecutioner.commandsExecuted) + '}' + self.cmdExecutioner.configuration.get('Shell', 'commandPrompt', fallback="(default conf) >>> ") )
              command = command.strip()

              

              # Check if we need to expand the command i.e. the command is either !!, ! or ^.
              # If so, expand it and return the expanded form.
              command = self.expandCommand(command)
              
              
              if len(command) == 0:
                 continue
              else:
                   print(command)  

              
              
              cParts = command.split()

              
              # Don't add history and quit commands to command history list
              # It clogs it.
              if cParts[0].lower() not in ['history', 'h', 'quit', 'q']:           
                 self.cmdHistory.addCommand( command )



              # NOTE: history/h command is the only command handled here!
              #       That's because the cHistory object is instantiated here
              # TODO: Check if there is a better design?
              if cParts[0] == 'history' or   cParts[0] == 'h':
                try:    
                 hArgs = ThrowingArgumentParser()
                 hArgs.add_argument('ncommands', nargs=argparse.REMAINDER, default='-1')
                 hArgs.add_argument('-s',  '--start', action='store_true')
                 args = vars( hArgs.parse_args(cParts[1:]) )
                except Exception as aEx:
                       print(str(aEx))
                       continue
                
                if len(args['ncommands']) == 0:
                    n = len(self.cmdHistory.commandHistory) 
                else:
                      try:
                         n = int( args['ncommands'][0] )
                         if n > len(self.cmdHistory.commandHistory):
                            n = len(self.cmdHistory.commandHistory)
                         elif n <= 0:
                              continue
                        
                      except Exception as convEx:
                            n = 0


                self.displayCommandHistory(n, args['start'])
                continue 



              # Execute command
              if self.cmdExecutioner.executeCommand( cParts ):                 
                 break

              

             except KeyboardInterrupt:
                 print("\nKeyboard interrupt seen.")


          # Save history 
          sts = self.cmdHistory.save()
          if sts != 0:
              print('Error', str(sts), 'writing .history file.')

          return


      
            


#
# Class to execute commands given
# via the application's shell
#
class shellCommandExecutioner:

      def __init__(self, cfg):
          self.configuration = cfg
          self.totalCommands = 0
          self.commandsExecuted = 0


      # Main entry point. Call this to execute commands given via the apps command line shell.
      # commandParts: a list of tokens comprising the command given, spearated by 
      #               whitespaces at the command line.
      #               For example, when the following is entered:
      #               TwitterAPI v2 >> search -t 1/1/1970 -u 2/1/1970 -t 0D12H5M3S -n 7 mmmmm
      #               commandParts will contain all tokens separated by whitespaces i.e.
      #               commandParts = ['search', '-t', '1/1/1970', '-u', '2/1/1970', '-t', '0D12H5M3S', '-n', '7', 'mmmmm']
      #               First item commandParts[0] is always the command and is used to call the method with the same
      #               name in this class.
      #               
      def executeCommand( self, commandPartsList):
          
          self.totalCommands += 1  
          if not hasattr(self, commandPartsList[0]):
             self.defaultF(commandPartsList[0])
             return(False)
            
          self.commandsExecuted += 1
          return getattr(self, commandPartsList[0])(commandPartsList[1:])  





      # Executes a command given as a string
      # TODO: This has not been tested at all.
      
      def executeCommandS( self, commandString ):
          # Split command at whitespace  
          return( self.executeCommand(commandString.split()) )
            



      # What to execute when no relevant method is found. 
      # I.e. command is not supported
      # NOTE: s is a string; NOT A LIST
      
      def defaultF(self, s):
          print('Invalid command', s)
          return(False)



      
      ###############################################################################
      #
      # This next section contains the implementation of ths supported shell
      # commands. All methods below are application specific as they implement the
      # behavior of various commands. I.e. the config method implements the
      # behavior of the config command given at the shell prompt.
      #
      # TODO: The methods below should be put in a different class based
      # on some behavioral (command???, strategy???) design pattern???
      # 
      ###############################################################################

      

      
      def q(self, a):
          return( True )
      
      def quit(self, a):
          return( True )
      
      
      def config(self, a):

          #Inline/nested function  
          def displayConfigSettings(cfg):
             if cfg is None:
                print('No configuration.')
                return          
          
             print("Configuration settings")
             for s in cfg.sections():
                 print("Section [", s, "]", sep="")
                 for key, value in cfg[s].items():
                     print( "\t-", key, "=", value)

          ####################################
          #  outer method config starts here
          ####################################
          
          print('Executing config >>>>>')
          displayConfigSettings(self.configuration)
          return(False)

          



      def get(self, a):
          try:  
             cmdArgs = ThrowingArgumentParser()          
             cmdArgs.add_argument('tweetids',   nargs=argparse.REMAINDER, default=[] )
             cmdArgs.add_argument('-f', '--idfile',  nargs='?', default='' )
             args = vars( cmdArgs.parse_args(a) )

          except Exception as gEx:
                print( str(gEx) )
                return(False)

          tAPI = twitterV2API.twitterSearchClient( self.configuration )
          if args['idfile'] == '':
             status = tAPI.getTweets( args['tweetids'] )
          else:
             if not os.path.exists( args['idfile'] ):
                print('Error. No such file [', args['idfile'], ']')
             else:
                idF = open( args['idfile'], 'r')
                #idList = idF.readlines()
                idList = mylist = idF.read().splitlines() 
                idF.close()
                print( 'File preview: ', idList[:5], '...\n', sep='' )
                status = tAPI.getTweets( idList + args['tweetids']  )   


          #if status is None:
          #   print('Error')
          





      def search(self, a):

          # Inner/nested function
          # Parses only arguments for search command ONLY.
          # Put in a different method in order not to bloat
          # the search method.
          def parseSearchArguments(cmdArgs):
        
            try:  
             parser = ThrowingArgumentParser()
          
             parser.add_argument('-f', '--from',   nargs='?', default= (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y") )
             parser.add_argument('-u', '--until', nargs='?', default=(datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y") )
             parser.add_argument('-t', '--timestep', nargs='?', default="" )
             parser.add_argument('-n', '--numtweets', type=int, nargs='?', default=0 )
             parser.add_argument('-o', '--outfile', type=str, nargs='?', default='' )
             parser.add_argument('-D',  '--debugmode', action='store_true')

             # IMPORTANT! The -S has been added to differentiate -in a quick and dirty manner-between period and simple queries.
             # if -S is present, this means a simple search will be conducted on the recent archive without any date constraints.
             # TODO: Get rid of -S and find some other way to differentiate these two type of queries 
             parser.add_argument('-S',  '--simple', action='store_true')

             # IMPORTANT! arguments -f, -u -t -n etc on the command line, MUST APPEAR BEFORE
             #            the remaining arguments. Otherwise, these arguments will not be parsed
             #            and will be interpreted as part of the remaining arguments i.e. parts of the query.
             parser.add_argument('keywords', nargs=argparse.REMAINDER)
          
          
             args = vars( parser.parse_args(cmdArgs) )

             # We make sure that no . spearator (separating seconds from ms at the end is present (as return by now())
             # this will destroy all our hypotheses about the formatting.
             # We also convert dates: Dates are always returned in isoformat.
             args['from'] = dateutil.parser.parse( args['from'].split('.')[0] , dayfirst=True).isoformat() + 'Z'        
             args['until'] = dateutil.parser.parse( args['until'].split('.')[0] , dayfirst=True).isoformat() + 'Z'    
             return(args)
    
            except Exception as argEx:
               print( str(argEx) )             
               return(None)
            
            return(None)


          ####################################
          #  outer method search starts here
          ####################################
          
          sParams = parseSearchArguments(a)
          if sParams is None:
             print("Usage: search [-f <from date>] [-u <to date>] [-n <number of tweets>] [-o <csv file>] [-S] [-D] <query>")
             return(False)

          
          # First, check if some configuration settings need to be overriden by
          # shell/command line arguments given by user. 
          # NOTE: We will make here a deep copy of the original configuration and make
          #       any change on that copy.
          # TODO: Check to see if Memento design pattern would be appropriate    


          
          # Before doing any change to the settings, make a deep copy of the current
          # config settings. This copy will be passed as
          # the search settings. Hence, any command shell arguments overrides the values
          # of the copy - not the original.
          # We consume a little bit of memory more, but
          # that's a static cost and is required memory is very, very low (i.e.
          # definitely within limits)
          # PS: We make a deep copy since we want to accommodate future modifications
          # where more complicate settings might be present in configurations. 
          cmdConfigSettings = copy.deepcopy( self.configuration )

         
          if sParams['numtweets'] != 0:
             cmdConfigSettings['General']['maxTweetsPerPeriod'] =  str(sParams['numtweets'])


          if sParams['outfile'] != '':
            if cmdConfigSettings.getboolean('Debug', 'debugMode', fallback=False):
               print("[DEBUG] Overriding setting csvFile from [", cmdConfigSettings['Storage']['csvFile'], "] to [", sParams['outfile'], "]")
             
            #cmdConfigSettings['Storage']['format'] =  'csv'
            cmdConfigSettings.set('Storage', 'format', 'csv')
            #cmdConfigSettings['Storage']['csvFile'] =  sParams['outfile']
            cmdConfigSettings.set('Storage', 'csvFile', sParams['outfile'])

          
        
          if sParams['debugmode']:
            #if configSettings.getboolean('Debug', 'debugMode', fallback=False):
            print("[DEBUG] Overriding setting debugMode from [", cmdConfigSettings['Debug']['debugMode'], "] to [", str(not cmdConfigSettings.getboolean('Debug', 'debugMode', fallback=False)), "]")
            # toggle debug setting
            cmdConfigSettings['Debug']['debugMode'] =  str( not cmdConfigSettings.getboolean('Debug', 'debugMode', fallback=False)) 

        

          # Perform actual search for tweets with the configuration. Instantiate an API object,
          tAPI = twitterV2API.twitterSearchClient( cmdConfigSettings )
          
          # Do we require a simple search on the recent archive, without any dates?
          if sParams['simple']:
             # Yes. This is a simple query without any dates. Call the appropriate method.   
             if cmdConfigSettings.getboolean('Debug', 'debugMode', fallback=False):
                print('[DEBUG] Initiating simple query on forced recent archive. No date constraints.')
                
             nFetched = tAPI.simpleQuery(  " ".join(sParams['keywords']).strip() )
          else:
             # This is a search based on dates. Call the appropriate method.   
             if cmdConfigSettings.getboolean('Debug', 'debugMode', fallback=False):
                print('[DEBUG] Initiating period query on specified archive. ')
                
             nFetched = tAPI.periodQuery( sParams['from'], sParams['until'], sParams['timestep'], " ".join(sParams['keywords']).strip() )

             
          if nFetched >= 0:
             print('\nFetched total of', nFetched, 'tweets.')
          else:
             print('\nError ', nFetched, 'encounterred.')   

                 
          return(False)





      def rawsearch(self, a):
          try:  
            parser = ThrowingArgumentParser()
            parser.add_argument('-e', '--endpointtweets', type=int, nargs='?', default=22 )
            parser.add_argument('-T','--twitterfields', nargs='+', default=['id', 'created_at'])
            parser.add_argument('-U','--userfields', nargs='+', default=['id', 'created_at'])

            parser.add_argument('qry', nargs=argparse.REMAINDER, default='')

            shellArgs = vars( parser.parse_args( a ) )
            
            #parser.add_argument('-f', '--from',   nargs='?', default= (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y") )
            #parser.add_argument('-u', '--until', nargs='?', default=(datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y") )
            #parser.add_argument('-t', '--timestep', nargs='?', default="" )
            
          except Exception as pEx:
                return(False)

          cmdConfigSettings = copy.deepcopy( self.configuration )


          cmdConfigSettings['TwitterAPI']['maxEndpointTweets'] =  str(shellArgs['endpointtweets'])
          print( cmdConfigSettings['TwitterAPI']['maxEndpointTweets']  )
          tAPI = twitterV2API.twitterSearchClient( cmdConfigSettings )

          
          response = tAPI.rawRequest( ' '.join(shellArgs['qry']).strip(), None, None, None)
          import json
          #parsed = json.loads(response)
          print(json.dumps(response, indent=4, sort_keys=True))
          
          #print(response)
          return(False)


      
      def showcsv(self, a):
          try:  
           shellParser = ThrowingArgumentParser()           
           shellParser.add_argument('-s', '--separator', nargs='?',  default=self.configuration.get('Storage', 'csvSeparator', fallback=',') )
           shellParser.add_argument('-n', '--numrows', type=int, nargs='?',  default=15)
           #shellParser.add_argument('-R', '--rows', nargs='?',  default=':')
           shellParser.add_argument('-N',  '--noheader', action='store_true')
           shellParser.add_argument('-T','--tail', action='store_true')
           shellParser.add_argument('-F','--fields', nargs='+', default=['username', 'url'])

           shellParser.add_argument('csvfile', nargs=argparse.REMAINDER, default='')

           shellArgs = vars( shellParser.parse_args( a ) )
           #print(shellArgs)
           #print('>>>',  shellArgs['csvfile'])
           if not shellArgs['csvfile']:
              # Empty. Fill in with default value from config file
              # We do this, since the REMAINDER option seems
              # to ignore default values in add_argument.
              # TODO: check this in a more thorough way
            shellArgs['csvfile'] = self.configuration.get('Storage', 'csvFile', fallback="data.csv")     
           else:   
              shellArgs['csvfile'] =  shellArgs['csvfile'][0]


      
          except Exception as ex:
             print( str(ex) )
             print("Invalid argument. Usage: showcsv [-F <field list>] [-s <separator>] [-N] [-n <number of rows>] [-T] <csv file name>")
             return(False)


          if not os.path.exists( shellArgs['csvfile'] ):
             print('File ', shellArgs['csvfile'], ' does not exist.' )
             from pathlib import Path
             p = Path(shellArgs['csvfile'])
             #print('Parent dir is [', p.parent, ']')
             if os.path.isabs( str(p.parent) ) or str(p.parent) == '.' :
                target = str(p.parent)
             else:      
                target = os.path.join(os.path.dirname(__file__), str(p.parent))             
                
             if not os.path.exists( target ):                
                return(False)   
             
             csvFiles = utils.listDirectoryFiles( target, '.csv') 
             if len(csvFiles) != 0:                  
                print('\nFound the following csv files in the same directory [', str(p.parent), '] which may be of interest to you (newest appear higher in list):', sep='')
                for fn in csvFiles:
                    if fn == '':
                       continue
                  
                    print('\t', fn, sep='')  
             
             return(False)
                
          
          hdr = 0  
          if shellArgs['noheader']:
             hdr = None
             
          try:             
             tweetsDF = pd.read_csv(shellArgs['csvfile'], sep=shellArgs['separator'], header=hdr )
             print('')
             print('File: ', shellArgs['csvfile'] )
             print('Number of rows:', tweetsDF.shape[0], sep='' )
             print('Number of columns:', tweetsDF.shape[1], sep='' )
             print('Column names:', list(tweetsDF.columns) )
             #print('Number of duplicate rows:', ) # TODO: Complete me.
             
             if not shellArgs['tail']:
                print('First ', shellArgs['numrows'], ' rows:', sep='')
                print( tweetsDF.loc[ :, shellArgs['fields'] ].head(shellArgs['numrows']) )
             else:
                 print('Last ', shellArgs['numrows'], ' rows:', sep='')
                 print( tweetsDF.loc[:, shellArgs['fields'] ].tail(shellArgs['numrows']) )      
                   
          except Exception as dfREx:
                print('ERROR.',  str(dfREx) )

          return(False)
            




      

      # TODO: Sorry about this. It's a mess. Needs to be seriously refactored.
      #       This was done quickly.
      def help(self, a):

            # Inner/nested function. Move this to utils???
            def NLFormat(string, every=72):
                lines = []
                for i in range(0, len(string), every):
                  lines.append('\t' + string[i:i+every])
                return '\n'.join(lines)
            
            print("\n\tSupported commands and their syntax:")
            print("")
            print('\t' + 72*'-')
            print( NLFormat('search [-f <date>] [-u <date>] [-t <time step>] [-D] [-S] [-o <csv file>] [-n <number of tweets/period>] <query>', 72) )
            print('\t'+72*'-')
            print('\tAbout:')
            print( NLFormat('     Performs a period search. Searches for tweets meeting conditions in <query> published between the dates specified in -f (from) and -u (until) arguments which is called a period. If -t , -u are missing, default date range is [two days ago - yesterday].  For a list of supported query operators see: https://developer.twitter.com/en/docs/twitter-api/v1/rules-and-filtering/search-operators . If -t option is specified then' +
                         ' the date range is divided into subranges according to the format specified by -t and search is conducted separately in each subrange. -n specifies how many' +
                         ' tweets to download during each subperiod. -o specifies the csv file to store tweets that meet the conditions. -D toggles the current debug mode on or off. -S conducts a simple search, i.e. a search on the recent archive with no date constraints.\n'))
            print( NLFormat('-n: Number of tweets to fetch. If a date query is conducted, -n specifies the number of tweets to download during each period.\n'))
            print( NLFormat( "-f, -u: Datetimes should be enterred as Day/Month/YearTHour:Minutes:Seconds. Datetimes are always in UTC. Example: search -f 29/12/2021T10:07:55 -u 31/12/2021T08:32:11 euro crisis\n" ))
            print( NLFormat( "-t: Time steps should be specified in the following manner: kDmHnMzS where k, m, n and z integer values. Example 3D10H5M8S. -t format specifies how the date range specified " +
                          " by -f and -u arguments will be divided into subperiods, in each of which a seperate search will be conducted for the same query. For example the query search -f 3/2/2008 -u 10/2/2008 -t 2D10H5M2S euro " +
                          " will break up the date range [3/2/2008, 10/2/2008] to subperiods of length 2 days, 10 hours, 5 minutes and 2seconfs and conduct a search in each of these perids. In this example, search " +
                          "for the term euro in tweets will be conducted in the following periods separately:"))
            print( NLFormat('[ 03/02/2008 00:00:00 - 05/02/2008 10:05:02 ]'))
            print( NLFormat('[ 05/02/2008 10:05:02 - 07/02/2008 20:10:04 ]'))
            print( NLFormat('[ 07/02/2008 20:10:04 - 10/02/2008 00:00:00 ]\n'))
            print( NLFormat('-S: Conduct a simple search. Simple search means that the recent archive is searched and that no date constraints are enforced. -S option will make any option related to dates such as -f, -u -t obsolete.\n'))
            print( NLFormat('-D: Toggle debug mode (if true, set to false. If false, set to true).\n'))
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
            return(False)
      
            

      


      def set(self, a):
          shellParser = ThrowingArgumentParser()
          try:
           shellParser.add_argument('-G', '--target', nargs='?', required=True, default='recent')
           shellArgs = vars( shellParser.parse_args( a ) )
          except Exception as ex:
             print("Invalid argument. Usage: set [-G] value")
             return(False)

          if shellArgs['target'].lower() == "recent":
             if 'TwitterAPI' in self.configuration.sections(): 
              self.configuration['TwitterAPI']['apiEndPoint'] =  self.configuration['TwitterAPI']['recentApiEndPoint']
              self.configuration['TwitterAPI']['bearer'] =  self.configuration['TwitterAPI']['essentialBearer']
              self.configuration['TwitterAPI']['targetArchive'] = 'recent'
              print("Target archive set to recent.")
          elif  shellArgs['target'].lower() == "historic":
                self.configuration['TwitterAPI']['apiEndPoint'] =  self.configuration['TwitterAPI']['historicApiEndPoint']
                self.configuration['TwitterAPI']['bearer'] =  self.configuration['TwitterAPI']['academicBearer']
                self.configuration['TwitterAPI']['targetArchive'] = 'historic'
                print("Target archive set to historic.")
          else:
             print("Invalid target archive option [", shellArgs['target'], "]. Allowed values: historic, recent", sep='')
             return(False)

     
          
  
      def reload(self, a):

        # Inner/nested function
        def setTargetArchive(cfg, md):
          if md.lower() == "recent":
            if 'TwitterAPI' in self.configuration.sections(): 
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


       ####################################
       #  outer method reload starts here
       ####################################
            
        shellParser = ThrowingArgumentParser()         
        try:
           shellParser.add_argument('-c', '--config',   nargs='?', default='')
           shellArgs = vars( shellParser.parse_args( a ) )
        except Exception as ex:
             print("Invalid argument. Usage: reload [-c config_file]")
             return(False)


        if shellArgs['config'] is None:
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




      def status(self, a):
          print('Status:')
          print('\tConfig file:', self.configuration.get('__Runtime', '__configSource', fallback="") )
          print('\tTarget search archive:', self.configuration.get('TwitterAPI', 'targetArchive', fallback="recent") )
          return(False)




      def encryptBearer(self, a):

          # Move this to utils?
          def NLFormat(string, every=72):
                lines = []
                for i in range(0, len(string), every):
                  lines.append('\t' + string[i:i+every])
                return '\n'.join(lines)


          try:
            parser = ThrowingArgumentParser()
            parser.add_argument('-V',  '--verify', action='store_true')
            args = vars( parser.parse_args(a) )

          except Exception as aEx:
                 print('ERROR!')
                 return(False)
            
          print( NLFormat('This command allows you to encrypt the bearer tokens (Essential and Academic) and use the encrypted tokens in configuration files.\n\n'))
          
          essB = input('\tGive the Essential bearer token to encrypt>>')
          acaB = input('\tGive the Academic bearer token to encrypt >>')
          
          encK, encEssB = utils.encrypt( essB )
          encAcaB = utils.encrypt2(encK, acaB)

          #print('Encrypting....')
          #print('Key:', encK, sep='')
          #print('Encoded Essential Bearer Token:', encEssB, sep='')
          #print('Encoded Academic Bearer Token:', encAcaB, sep='')

          while True:
             kF = input('\tGive the local file to store the encryption key >>')
             if kF.strip() != '':
                try:   
                  keyFile = open(kF, "wt")
                  n = keyFile.write(encK)
                  keyFile.close()
                  break
                except Exception as wEx:
                       print( str(wEx) )
                       print('Could not write file [', kF, ']')
                       continue
                
          print(NLFormat('\n\tPlease follow now the next step to complete the process:') )
          
          print(NLFormat('\n\tUpdate the configuration file with the following settings:') )
          print('')
          print(NLFormat('\t\tessentialBearer = ' + encEssB, every=1012) )
          print(NLFormat('\t\tacademicBearer = ' + encAcaB, every=1012))
          print(NLFormat('\t\tencryptionKeyFile = ' +  kF) )
          print(NLFormat('\t\tbearerEncrypted = true') )
          print('')
          print('')
          if args['verify']:
             print('\tVerifying:')   
             print('\t\tVerifying essential bearer....', end='')
             if utils.decrypt( encK, encEssB ) == essB:
                print('OK')
             else:
                print('ERROR')

             print('\t\tVerifying academic bearer....', end='')
             if utils.decrypt( encK, encAcaB ) == acaB:
                print('OK')
             else:
                print('ERROR')
             
          #print('\tDecoded Essential Bearer:', utils.decode( encK, encEssB ), sep='')
          #print('\tDecoded Academic Bearer:', utils.decode( encK, encAcaB ), sep='')

          
          return(False)

