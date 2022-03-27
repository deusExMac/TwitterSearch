
clc = 0
def f(string,  every=26, prefix='', startOver=False):
    global clc
    
    rest = every - clc
    if clc == 0:
       print( '\t[',string[ :min(len(string), rest)], ']', sep='', end='')
    else:
       print( '[',string[ :min(len(string), rest)], ']', sep='', end='')

    clc = clc + min(len(string), rest)
    strPos = min(len(string), rest)
    #print('clc=', clc)
    if clc >= every:
       print('')
       clc = 0
       
    lst = 0
    #print('Starting at ', printed, ' for ', string, sep='')
    for i in range( strPos, len(string), every):
        #print('Starting', clc, 'until', i+every )
        print('\t',  prefix, string[i:i+every], sep='', end='')
        lst =len(string[i:i+every])

    clc = lst
    
    '''
    if rest != 0:
       print(string[clc:clc + rest], sep='', end='')
    else:
       print('\t', string[:clc + rest], sep='', end='')

    # TODO: Fix this
    clc = clc + min(len(string), rest)
    print(clc, end='')
    
    return
    '''


    '''
    if clc >= every:
       print('')
       #clc = 0
       
    if len(string) >= rest:
       print('')
       #clc=0
    else:   
       return
    
    #print('P:', clc)
    
     
    lst = 0
    for i in range( clc, len(string), every):
        #print('Starting', clc, 'until', i+every )
        print('\t',  prefix, string[i:i+every], sep='')
        lst =len(string[i:i+every]) 

    #print('clc=', clc, 'last=', lst) 
    clc = lst
    #return('')
    '''


#f('manolismanolismanolisjdajskdljaskljdklasjdklasjdklajsdkljasdkljaskldjsalkjslk1', every=7)
for i in range(13):
    f('hhhhX', every=4)
    
print('\n\nclc=', clc)






############
#
# Next running fine
#


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

def formatAlignment(string,  every=26, prefix='', startOver=False):

     # How many charcters have been printed on the
     # current line
     global currentLineChars
     
     lines = []

     if startOver:        
        lines.append('\n')
        currentLineChars = 0
        
          

     # Does string fit into the rest of line?
     if len(string) + currentLineChars  <= every:
        #print('less than every') 
        if currentLineChars == 0:
           #print('Appending [', prefix, string,']')
           if len(string) > 0: 
              lines.append('\t' + prefix + string)
           #else:
           #   lines.append(prefix + string) 
           #print(lines)
        else:           
            lines.append(string)
           
        currentLineChars = len(string) + currentLineChars 
        if currentLineChars == every:
           currentLineChars = 0 
           return("\n".join(lines) + '\n')
        
        # TODO: if first is newline, return length of second element
        return("\n".join(lines)) 

     # No, does not fit. Break it apart in chunks of size every
     # after having filled the space in existing line.

     # TODO: Do we REALLY need next if statement????
     if currentLineChars == 0:         
         lines.append( '\t' + prefix + string[:(every - currentLineChars)])
     else:
         # fill in remaining line
         lines.append( string[:(every - currentLineChars)])


     # Fill out complete lines
     for i in range(every-currentLineChars, len(string), every):
     #for i in range(0, len(string), every):    
         lines.append('\t' + prefix + string[i:i+every])

     # TODO: alternative expression len( lines[-1] - ( len(prefix) + 1 )
     currentLineChars = len(lines[-1]) - 1 - len(prefix)    
     return '\n'.join(lines)






'''
print( formatAlignment('This is an example', every=45), end='' )
print( formatAlignment('FUCK YOU TOOOOOOO               X', every=45), end='' )
#print( formatAlignment('', prefix='', startOver=True), end='' )
#print( formatAlignment('', prefix='', startOver=True), end='' )
#print( formatAlignment('', prefix='', startOver=True), end='' )
print( formatAlignment('This',  startOver=False), end='' )
print( formatAlignment('',  startOver=True), end='' )

for i in range(295):
    print( formatAlignment('.', prefix='  ', every=33), end='' )

#print( formatAlignment('', prefix='', startOver=True), end='' )
print( formatAlignment('Hello there!', prefix='', startOver=True), end='' )
for i in range(12):
    print( formatAlignment('X', prefix=' ', every=34), end='' )
print( formatAlignment('K', prefix='', startOver=True), end='' )
print( formatAlignment('L', prefix='', startOver=False), end='' )
print( '\n\n=', currentLineChars )  
'''
