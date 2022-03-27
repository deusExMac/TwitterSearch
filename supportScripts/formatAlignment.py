
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
def fL(string,  every=26, prefix='', startOver=False):
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

    
    
    '''    
    lst = 0
    #print('Starting at ', strPos, ' for ', string, sep='')
    for i in range( strPos, len(string), every):
        #print('Starting', clc, 'until', i+every )
        print('\t*',  prefix, string[i:i+every], '*', sep='', end='')
        if len() >= len(string):
           print('', i) 
        lst =len(string[i:i+every])

    if lst == every:
       #print('') 
       clc = 0
    else:   
       clc = lst
    '''   
    




#f('manolismanolismanolisjdajskdljaskljdklasjdklasjdklajsdkljasdkljaskldjsalkjslk1', every=7)
'''
for i in range(91):
    if i%2 == 0:
       f('z', every=7)
    else:
       f('X', prefix=' ', every=7)
       
    #print('clc=', clc)
f('X', every=2)
'''


#print(fL(' Happy families are all alike; every unhappy family is unhappy in its own way. Everything was in confusion in the Oblonskys’ house. The wife had discovered that the husband was carrying on an intrigue with a French girl, who had been a governess in their family, and she had announced to her husband that she could not go on living in the same house with him. This position of affairs had now lasted three days, and not only the husband and wife themselves, but all the members of their family and household, were painfully conscious of it. Every person in the house felt that there was no sense in their living together, and that the stray people brought together by chance in any inn had more in common with one another than they, the members of the family and household of the Oblonskys. The wife did not leave her own room, the husband had not been at home for three days. The children ran wild all over the house; the English governess quarreled with the housekeeper, and wrote to a friend asking her to look out for a new situation for her; the man-cook had walked off the day before just at dinner time; the kitchen-maid, and the coachman had given warning. Three days after the quarrel, Prince Stepan Arkadyevitch Oblonsky—Stiva, as he was called in the fashionable world—woke up at his usual hour, that is, at eight o’clock in the morning, not in his wife’s bedroom, but on the leather-covered sofa in his study. He turned over his stout, well-cared-for person on the springy sofa, as though he would sink into a long sleep again; he vigorously embraced the pillow on the other side and buried his face in it; but all at once he jumped up, sat up on the sofa, and opened his eyes. ', every=81))


#print(fL('hahahaha', every=6))

print( fL('Hello there!', startOver=False, prefix=' ', every=16), end='' )
print( fL('', startOver=True, prefix=' ', every=16), end='' )
for i in range(23):
    print(fL('.', prefix='', every=17),end='')
#print( fL('', startOver=True), end='' )
print( fL('Hello there!', startOver=True, prefix=' ', every=2), end='' )
#print( fL('Stepan Arkadyevitch was a truthful man in his relations with himself. He was incapable of deceiving himself and persuading himself that he repented of his conduct. He could not at this date repent of the fact that he, a handsome, susceptible man of thirty-four, was not in love with his wife, the mother of five living and two dead children, and only a year younger than himself. All he repented of was that he had not succeeded better in hiding it from his wife. But he felt all the difficulty of his position and was sorry for his wife, his children, and himself. Possibly he might have managed to conceal his sins better from his wife if he had anticipated that the knowledge of them would have had such an effect on her. He had never clearly thought out the subject, but he had vaguely conceived that his wife must long ago have suspected him of being unfaithful to her, and shut her eyes to the fact. He had even supposed that she, a worn-out woman no longer young or good-looking, and in no way remarkable or interesting, merely a good mother, ought from a sense of fairness to take an indulgent view. It had turned out quite the other way.', every=78), end='')

'''
print(fL('', startOver=True))
print(fL('FUCK YOU TOO!', every=6, startOver=True) )
'''

print('\n\nclc=', clc)
    
###########################################
    
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
