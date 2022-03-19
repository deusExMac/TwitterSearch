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

# We define constants in this file
import appConstants
from commandHistory import commandHistory
import twitterV2API 




# The following two classes are used to parse
# arguments on the shell 'scommand line
class ArgumentParserError(Exception): pass
  
class ThrowingArgumentParser(argparse.ArgumentParser):
      def error(self, message):
          raise ArgumentParserError(message)






class commandShell:

      def __init__(self, cfg):
          self.configuration = cfg
          #self.totalCommands = 0
          #self.commandsExecuted = 0
          self.cmdExecutioner = shellCommandExecutioner(cfg)
          self.cmdHistory = commandHistory(self.configuration.getint('Shell', 'historySize', fallback=10), True)




      def startShell(self):

          while True:
             try:
              command = input('{' + str(self.cmdExecutioner.commandsExecuted) + '}' + self.configuration.get('General', 'commandPrompt', fallback="(default conf) >>> ") )
              command = command.strip()
    
              if len(command) == 0:
                 continue   

              # Don't add history and quit commands to command history list
              # It clogs it.
              if command.lower() not in ['history', 'h', 'quit', 'q']:           
                 self.cmdHistory.addCommand( command )

              cParts = command.split()

              # NOTE: history/h command is the only command executed here!
              #       That's because the cHistory object is instantiated here
              # TODO: Check if there is a better design?
              if cParts[0] == 'history' or   cParts[0] == 'h':
                 self.cmdHistory.printHistory()
                 continue 

              
              if self.cmdExecutioner.executeCommand( cParts ):                 
                 break

             except KeyboardInterrupt:
                 print("\nKeyboard interrupt seen.")


          sts = self.cmdHistory.save()
          if sts != 0:
              print('Error', str(sts), 'writing history file.')

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



      
      ######################################################################
      # All methods below are application specific as they implement the
      # behavior of various commands.
      #
      # TODO: The methods below should be put in a different class based
      # on some behavioral (command???, strategy???)  or structural design
      # pattern.
      ######################################################################

      

      
      def q(self, a):
          return( True )
      
      def quit(self, a):
          return( True )
      
      
      def config(self, a):

          #Inlide/nested function  
          def displayConfigSettings(cfg):
             if cfg is None:
                print('No configuration.')
                return

          ####################################
          #  outer method config starts here
          ####################################
          
             print("Configuration settings")
             for s in cfg.sections():
                 print("Section [", s, "]", sep="")
                 for key, value in cfg[s].items():
                     print( "\t-", key, "=", value)
                     
          print('Executing config >>>>>')
          displayConfigSettings(self.configuration)
          return(False)

          

                 


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

             # IMPORTANT! arguments -f, -u -t -n etc on the command line, MUST APPEAR BEFORE
             #            the remaining arguments. Otherwise, these arguments will not be parsed
             #            and will be part of the remaining arguments.
             parser.add_argument('keywords', nargs=argparse.REMAINDER)
          
          
             args = vars( parser.parse_args(cmdArgs) )

             # We make sure that no . spearator (separating seconds from ms at the end is present (as return by now())
             # this will destroy all our hypotheses about the formatting.
             # Dates are always returned in isoformat.
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
             print("Usage: search [-f <from date>] [-u <to date>] [-n <number of tweets>] [-o <csv file>] [-D] <query>")
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
             
            cmdConfigSettings['Storage']['csvFile'] =  sParams['outfile']

          
        
          if sParams['debugmode']:
            #if configSettings.getboolean('Debug', 'debugMode', fallback=False):
            print("[DEBUG] Overriding setting debugMode from [", cmdConfigSettings['Debug']['debugMode'], "] to [", str(not cmdConfigSettings.getboolean('Debug', 'debugMode', fallback=False)), "]")
            # toggle debug setting
            cmdConfigSettings['Debug']['debugMode'] =  str( not cmdConfigSettings.getboolean('Debug', 'debugMode', fallback=False)) 

        

          # Perform actual search for tweets with the configuratio.
          tAPI = twitterV2API.twitterSearchClient( cmdConfigSettings )
          nFetched = tAPI.query( sParams['from'], sParams['until'], sParams['timestep'], " ".join(sParams['keywords']).strip() ) 
          if nFetched >= 0:
             print('\nFetched total of', nFetched, 'tweets.')
          else:
             print('\nError ', nFetched, 'encounterred.')   

                 
          return(False)



      

      # TODO: Sorry about this. It's a mess. Needs to be seriously refactored.
      #       This was done quickly.
      def help(self, a):

            # Inner/nested function
            def NLFormat(string, every=72):
                lines = []
                for i in range(0, len(string), every):
                  lines.append('\t' + string[i:i+every])
                return '\n'.join(lines)
            
            print("\n\tSupported commands and their syntax:")
            print("")
            print('\t' + 72*'-')
            print( NLFormat('search [-f <date>] [-u <date>] [-t <time step>] [-D] [-o <csv file>] [-n <number of tweets/period>] <query>', 72) )
            print('\t'+72*'-')
            print('\tAbout:')
            print( NLFormat('     Performs a period search. Searches for tweets meeting conditions in <query> published between the dates specified in -f (from) and -u (until) arguments which is called a period. If -t , -u are missing, default date range is [two days ago - yesterday].  For a list of supported query operators see: https://developer.twitter.com/en/docs/twitter-api/v1/rules-and-filtering/search-operators . If -t option is specified then' +
                         ' the date range is divided into subranges according to the format specified by -t and search is conducted separately in each subrange. -n specifies how many' +
                         ' tweets to download during each subperiod. -o specifies the csv file to store tweets that meet the conditions. -D toggles the current debug mode on or off.'))
            print( NLFormat( "-f, -u: Datetimes should be enterred as Day/Month/YearTHour:Minutes:Seconds. Datetimes are always in UTC. Example: search -f 29/12/2021T10:07:55 -u 31/12/2021T08:32:11 euro crisis" ))
            print( NLFormat( "-t: Time steps should be specified in the following manner: kDmHnMzS where k, m, n and z integer values. Example 3D10H5M8S. -t format specifies how the date range specified " +
                          " by -f and -u arguments will be divided into subperiods, in each of which a seperate search will be conducted for the same query. For example the query search -f 3/2/2008 -u 10/2/2008 -t 2D10H5M2S euro " +
                          " will break up the date range [3/2/2008, 10/2/2008] to subperiods of length 2 days, 10 hours, 5 minutes and 2seconfs and conduct a search in each of these perids. In this example, search " +
                          "for the term euro in tweets will be conducted in the following periods separately:"))
            print( NLFormat('[ 03/02/2008 00:00:00 - 05/02/2008 10:05:02 ]'))
            print( NLFormat('[ 05/02/2008 10:05:02 - 07/02/2008 20:10:04 ]'))
            print( NLFormat('[ 07/02/2008 20:10:04 - 10/02/2008 00:00:00 ]'))
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


