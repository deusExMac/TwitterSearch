import datetime
import dateutil.parser
from datetime import datetime, timedelta
import configparser





#
# Generates periods based on steps specified by t
# NOTE: from date f, until date u must be strings
# formatted in ISO time (format %Y-%m-%dT%H:%M:%SZ).
#
def generateSubperiods(f, u, t, cfg=None ):

      
      # Configuration is required
      if cfg is None:
         return(None)

        
      tPeriods = []
    
      if datetime.strptime(f, "%Y-%m-%dT%H:%M:%SZ") > datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ"):
       print('Invalid dates: End-date [', u, '] must be after start-date [', f, ']') 
       return(None)
      
      if t == "":
       tPeriods.append( {'from': f, 'until': u} )
       if cfg.getboolean('Debug', 'debugMode', fallback=False):  
          print("\t[DEBUG] No time step specified. Adding SINGLE search period: [", datetime.strptime(f, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M:%S"), "-", datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M:%S"), "]")

       return(tPeriods)

      # Do some normalization if needed
      # TODO: Check this! It has not been tested
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


      if cfg.getboolean('Debug', 'debugMode', fallback=False):
         print('[DEBUG] day=', dayVal, 'hours=', stepValue.hour, 'minute=', stepValue.minute, 'seconds=', stepValue.second)

      # If for some strange reason all values are 0, don't break up period   
      if (dayVal == 0 and stepValue.hour == 0 and stepValue.minute == 0 and stepValue.second==0):
          if cfg.getboolean('Debug', 'debugMode', fallback=False):
             print('[DEBUG] Zero values in time step (', t, ')')
             
          tPeriods.append( {'from': f, 'until': u} )
          return(tPeriods)
            
           
      sDate = datetime.strptime(f, "%Y-%m-%dT%H:%M:%SZ")
      pCnt = 0
      while True:
        eDate = sDate + timedelta(days= dayVal, hours = stepValue.hour, minutes = stepValue.minute, seconds=(stepValue.second) )                                                            
        if eDate >= datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ"):
           eDate = datetime.strptime(u, "%Y-%m-%dT%H:%M:%SZ")
           tPeriods.append( {'from': sDate.strftime("%Y-%m-%dT%H:%M:%SZ"), 'until': eDate.strftime("%Y-%m-%dT%H:%M:%SZ")} )
           pCnt += 1
           if cfg.getboolean('Debug', 'debugMode', fallback=False):
              print("\t[DEBUG] Adding search period: [", sDate.strftime("%d/%m/%Y %H:%M:%S"), "-", eDate.strftime("%d/%m/%Y %H:%M:%S"), "]")
              
           return(tPeriods)
      
        if cfg.getboolean('Debug', 'debugMode', fallback=False):
           print("\t[DEBUG] Adding search period: [", sDate.strftime("%d/%m/%Y %H:%M:%S"), "-", eDate.strftime("%d/%m/%Y %H:%M:%S"), "]")
           
        tPeriods.append( {'from': sDate.strftime("%Y-%m-%dT%H:%M:%SZ"), 'until': eDate.strftime("%Y-%m-%dT%H:%M:%SZ")} )
        pCnt += 1
        sDate = sDate + timedelta(days= dayVal, hours = stepValue.hour, minutes = stepValue.minute, seconds=stepValue.second)

      # TODO: Remove this?
      return(tPeriods)


 
# TODO: Check and use this?
def NLFormatString(string, every=72):
    lines = []
    for i in range(0, len(string), every):
        lines.append('\t' + string[i:i+every])

    return '\n'.join(lines)






# 
# Function formatAlignment formats string messages to be printed
# on the screen as right and left aligned, as the example below:
#
#       .(72/72/72/33.59).(72/72/144/44.39).(72/72/216/46.04).(7
#	2/72/288/47.96).(72/72/360/48.39).(72/72/432/52.74).(72/
#	72/504/52.48).(72/72/576/52.41).(72/72/648/53.91).(72/72
#	/720/53.80).(72/72/792/57.08).(72/72/864/59.74).(72/72/9
#	36/61.53).(72/72/1008/61.32).(72/72/1080/60.90).(72/72/1
#	152/60.10).(72/72/1224/60.30).(72/72/1296/60.34).(72/72/
#	1368/60.19).(72/72/1440/60.03).(72/72/1512/59.44).(72/72
#	/1584/59.75).(72/72/1656/59.59).(72/72/1728/59.24).(72/7    
#
# It can do this for sucessive calls of the function
#
# TODO: Function has not been thoroughly tested. It has been sloppy
#       written and must be optimized.
#

# This is a very important global variable
# required by formatAlignment to keep track of how many
# characters have been printed on the current line.
#
# Pls don't remove it or change its initialization value

currentLineChars = 0

def formatAlignment(string,  every=56, startOver=False):

     # How many charcters have been printed on the
     # current line
     global currentLineChars
     
     lines = []

     if startOver:        
        lines.append('\n')
        currentLineChars = 0
        
          

     # Does string fit into the rest of line?
     if len(string) + currentLineChars  <= every:
        if currentLineChars == 0:            
           lines.append('\t' + string)
        else:           
            lines.append(string)

        #print(currentLineChars, end='')   
        currentLineChars = len(string) + currentLineChars 
        if currentLineChars == every:
           currentLineChars = 0 
           return(lines[0] + '\n')
        
        return(lines[0]) 

     # No, does not fit. Break it apart in chunks of size every
     # after having filled the space in existing line.
     
     if currentLineChars == 0:         
         lines.append( '\t' + string[:(every - currentLineChars)])
     else:            
         lines.append( string[:(every - currentLineChars)])

     
     for i in range(every-currentLineChars, len(string), every):
         lines.append('\t' + string[i:i+every])
     
     currentLineChars = len(lines[-1])-1    
     return '\n'.join(lines)
  



###############
#
# Two new versions f and fL .
# TODO: TEST THE THOROUGHLY!!!!!
#


#Current line count
clc = 0
def f(string,  every=26, prefix='', startOver=False):
    global clc

    if startOver:
       print('')
       clc = 0

       
    rest = every - clc
    if clc == 0:
       print( '\t', prefix, string[ :min(len(string), rest)],  sep='', end='')
    else:
       print(  string[ :min(len(string), rest)],  sep='', end='')

    clc = clc + min(len(string), rest)
    strPos = min(len(string), rest)
    #print('clc=', clc)
    if clc >= every:
       print('')
       clc = 0

    if len(string) <= strPos:
       return
        
       
    # This means that length of string is greater than line length.
    numCompleteLines = len( string[strPos:] ) // every
    lastLineChars = len( string[strPos:] ) % every

    i = strPos
    s = 0
    e = strPos
    for k in range(numCompleteLines):
        s = strPos + k*every
        e = s + every
        print('\t',  prefix, string[s:e],  sep='')

    if lastLineChars == 0:
       clc = 0
    else:   
       print( '\t', prefix, string[e:], sep='', end='')
       clc = len(string[e:])

    return



#Current line count
#clc = 0
def fL(string,  every=57, prefix='', startOver=False):
    global clc

    lines = []
    if startOver:
       if clc != 0: 
          #print('')
          lines.append('') #add empty string to force newline at beginning
       clc = 0

       
    rest = every - clc
    if clc == 0:
       lines.append( '\t'+ prefix + string[ :min(len(string), rest)] )
    else:
       lines.append(    string[ :min(len(string), rest)]  )

    clc = clc + min(len(string), rest)
    strPos = min(len(string), rest)

    #print('clc=', clc, 'every=', every, 'strPos=', strPos, end='')
    if clc >= every:
       #lines.append('')
       clc = 0

    if len(string) <= strPos:
       #print('[' +'ppp'.join(lines) + ']')
       #print('returning without enter at end', end='')
       if clc==0: 
          return( '\n'.join(lines)+'\n' )
       else:
          return( '\n'.join(lines)) 
        
    
    # This means that length of string is greater than line length.
    numCompleteLines = len( string[strPos:] ) // every
    lastLineChars = len( string[strPos:] ) % every
    #print('numCom=', numCompleteLines, 'lastlineChars=', lastLineChars, end='')
    
    i = strPos
    s = 0
    e = strPos
    for k in range(numCompleteLines):
        s = strPos + k*every
        e = s + every
        lines.append('\t' +  prefix + string[s:e] )

    if lastLineChars == 0:
       #lines.append('\n') 
       clc = 0
       #print(lines)
       return( '\n'.join(lines)+ '\n' )
    else:   
       lines.append( '\t' + prefix + string[e:])
       clc = len(string[e:])
       return( '\n'.join(lines) )

     

