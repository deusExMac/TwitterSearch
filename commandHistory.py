


"""

Module containing command history that stores commands given
by the user via the application shell.



Author: mmt
Version: 20/04/2022

"""



import os

class commandHistory:

      def __init__(self):
          self.commandHistory = []
          self.historySize = 15
          self.saveToFile = True
          self.historyFile = '.history'
          self.load()


      def __init__(self, hS, sF, fN='.history'):
          self.commandHistory = []
          self.historySize = hS
          self.saveToFile = sF
          self.historyFile = fN
          self.load()


      def setHistorySize(self, nS):
           self.historySize = nS           
           if len(self.commandHistory) > nS:
              for i in range( len(commandHistory) - nS):
                  self.commandHistory.pop(0)  
                      

      def addCommand(self, cmd):
          if self.historySize > 0 :
            if len(self.commandHistory) >= self.historySize :
               self.commandHistory.pop(0)
                      
          self.commandHistory.append(cmd)
          
          
      def get(self, idx):
          if len(self.commandHistory) < idx:
             return ""

          return(self.commandHistory[idx -1])


      def getLast(self):
          if len(self.commandHistory) <= 0:
             return('')

          return( self.commandHistory[-1] )  
      



      def getN(self, n, fromBegin=False):
          if fromBegin:
             return( self.getFirstN(n) )

          return( self.getLastN(n) )  





      # Return list with last n commands in history
      def getFirstN(self, n):
          if n <= 0:
             return( [] )
            
          if len(self.commandHistory) <= n:
             endPos = len(self.commandHistory)    
          else:  
             endPos = n

          return( self.commandHistory[:endPos] )




      # Return list with last n commands in history
      def getLastN(self, n):
          if n <= 0:
             return( [] )
            
          if len(self.commandHistory) <= n:
             startPos = 0    
          else:  
             startPos = -n

          return( self.commandHistory[startPos:] )   




      def getLastStartingWith(self, strt):

          if len(strt) == 0:
             return('')
            
          for cmd in self.commandHistory[::-1]:
              if cmd.startswith(strt):
                 return(cmd)
            
          return('')


      
          
      def load(self):
        #print('Loading history file:', self.historyFile)    
        if os.path.exists(self.historyFile):
              #print("Loading shell history\n")  
          with open(self.historyFile, 'r') as histFile:
               self.commandHistory = [cmd.rstrip() for cmd in histFile.readlines()]

          # in case historySize if set to a smaller amount than actual size
          # prune history by removing oldest commands.
          if len(self.commandHistory) > self.historySize:
              diff = len(self.commandHistory) - self.historySize
              for d in range(diff):
                  self.commandHistory.pop(0)


      def save(self):          
          if self.saveToFile:
           try:     
             with open(self.historyFile, 'w') as histFile:
                 histFile.writelines("%s\n" % cmd for cmd in self.commandHistory)
             return(0)
           except Exception as hWEx:
                 print( 'ERROR:', str(hWEx) )
                 return(-23)
