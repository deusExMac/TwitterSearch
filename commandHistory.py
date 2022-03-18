
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

          return( self.get(len(self.commandHistory)) )  
      

        
      def printHistory(self):
          cPos = 1
          for c in self.commandHistory:
              print(cPos, ". ", c, sep="")
              cPos += 1
              
          
      def load(self):
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
                 return(-23)
