
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
          #print(self.commandHistory)
          
      def get(self, idx):
          if len(self.commandHistory) < idx:
             return ""

          return(self.commandHistory[idx -1])

        
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


      def save(self):
          #print("Saving history file")
          if self.saveToFile:
           with open(self.historyFile, 'w') as histFile:
               histFile.writelines("%s\n" % cmd for cmd in self.commandHistory)
               
