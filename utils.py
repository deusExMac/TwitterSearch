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


