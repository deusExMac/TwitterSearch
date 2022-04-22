

#################################################################################################################################################
#
# TwitterSearch
#
# A simple python program that allows querying and downloading tweets using the Twitter v2 API.
# The sole puprose of this is to experiment with and get to know Twitter's v2 API.
# This is experimental and has been created without much thought. It has not been properly designed. It has not been tested thoroughly.
# Any design error or bugs manifested are exclusively my own fault.
#
# Please have mercy.
#
#
# IMPORTANT! See the README on Github on how to prepare and execute TwitterSearch.
#
# The developed was based on the source code found here:
#    https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
#
# TODO: This has been created in a hurry. Has not been tested thoroughly.
#       Needs serious refactoring.
#
# Internal version info:
#          v0.85b mmtrd20/04/2022
#          v0.82b mmtrd30/03/2022
#          v0.77b mmtrd18/03/2022
#          v0.4b mmtrd31/12/2021
#
#################################################################################################################################################


"""

Module containing main program. Execution starts from here.



Author: mmt
Version: 20/04/2022

"""


import sys
import os

import configparser
import argparse


# We define constants in this file
import appConstants
import commandShell




# Generate an empty configuration, with only the sections.
# Used when no valud configuration file is given or found.
def generateDefaultConfiguration():
    cS = configparser.RawConfigParser(allow_no_value=True)
    cS.add_section('General')
    cS.add_section('Network')
    cS.add_section('TwitterAPI')
    cS.add_section('Request')
    cS.add_section('Storage')
    cS.add_section('Shell')
    cS.add_section('Debug')
    return(cS)
    


def setTargetArchive(cfg, md):
    if md.lower() == "recent":
       if 'TwitterAPI' in cfg.sections():
           cfg.set('TwitterAPI', 'apiEndPoint', cfg.get('TwitterAPI', 'recentApiEndPoint', fallback='XXXXX') )           
           cfg.set('TwitterAPI', 'bearer', cfg.get('TwitterAPI', 'essentialBearer', fallback='YYYYYY') )           
           cfg.set('TwitterAPI', 'targetArchive', 'recent')
           
           print("\tTarget archive set to recent.")
           return(0)
    elif  md.lower() == "historic":
          cfg.set('TwitterAPI', 'apiEndPoint', cfg.get('TwitterAPI', 'historicApiEndPoint', fallback='ZZZZZZ') )          
          cfg.set('TwitterAPI', 'bearer', cfg.get('TwitterAPI', 'academicBearer', fallback='AAAAAA') )          
          cfg.set('TwitterAPI', 'targetArchive', 'historic' )          
          print("\tTarget archive set to historic.")
          return(0)
    else:
          print("\tInvalid target archive option [", md, "] in configuration file. Use historic or recent.", sep='')
          return(-4)

        


  

         


#
# If you are using older version of IDLE (Python 3.x.x) on MacOS
# uncomment next line to specify command line argument:
#
# sys.argv = [sys.argv[0], '-c', 'twitterSearch.conf']
#





######################################################################
#
#
# Program starts here
#
#
######################################################################


cmdArgParser = argparse.ArgumentParser(description='Command line arguments')
cmdArgParser.add_argument('-c', '--config',   default=appConstants.DEFAULTCONFIGFILE)
args = vars( cmdArgParser.parse_args() )



# Config file that will be used
configFile = args['config']

print('')
print('Python v', sys.version)
print("")      
print('TwitterSearch v'+appConstants.APPVERSION, 'rd', appConstants.VERSIONRELEASEDATE )



# Note: We use .RawConfigParser() because some configuration strings contain special chars like % that
#       have special meaning for the ConfigParser class
configSettings = configparser.RawConfigParser(allow_no_value=True)

 
print('\tLoading configuration file [', configFile, ']........', sep='', end='')

# Load config file
if not os.path.exists(configFile):
   print("ERROR. File not found. Continuing with default settings.", sep="")
   configSettings = generateDefaultConfiguration()
   
else:
   try:        
    configSettings.read(configFile)
    configSettings.add_section('__Runtime')
    configSettings['__Runtime']['__configSource'] = configFile  
    print('OK', sep="")
   except Exception as cfgEx:
      print(str(cfgEx)) 
      print('Error reading file [', configFile, ']. Continuing with default settings.', sep="")
      configSettings = generateDefaultConfiguration()
      
    



# Set the proper bearer token depending on the value of target archive (Allowed values: recent, historic).
# Invalid target archive values result in termination.
sts = setTargetArchive(configSettings, configSettings.get('TwitterAPI', 'targetArchive', fallback="recent") )
if sts != 0:
   print('Fatal error. Terminating.')
   sys.exit()

print("\nType 'help' to see a list of supported commands.\n")



# Everything looks fine. Start the TwitterSearch command shell through which the user
# may execute commands.
# Control is now transferred to the shell
appShell = commandShell.commandShell( configSettings )
appShell.startShell()


print("\nFinished. ByeBye!")


