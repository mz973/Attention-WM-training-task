<<<<<<< HEAD
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:45:48 2017
@author: mz
A test of stimulus similarity
"""

#imports
from psychopy import visual,core,gui,event
from datetime import datetime
import itertools, csv
from random import shuffle
import numpy as np


win = visual.Window([900,900],fullscr=False,allowGUI=True) #psychopy window
c = 0.2 # mean N/T similarity 0< c <0.2
d1=0.2; # D1/T similarity 0< d1 <c
d2 = [2*c-d1,d1-2*c]
p = [abs(d1-d2[0]), abs(d1-d2[1])] # N/N similarity
print('mean N/T similarity: ',c)
print('N/N similarity: ',p)

def make_stim (Type, pos=(0,0),size=0.15, lw=2.5):
    angle =-30
    stimVert1 = [(0, 0), (.2, 0), (.2, .4),(.2, 0),(.4,0)] #target
    stimVert2 = [(0, 0), (.2-d1, 0), (.2-d1, .4),(.2-d1, 0),(.4,0)] #d1
    stimVert3 = [(0, 0), (.2-d2[0], 0), (.2-d2[0], .4),(.2-d2[0], 0),(.4,0)] #d2_1
    stimVert4 = [(0, 0), (.2-d2[1], 0), (.2-d2[1], .4),(.2-d2[1], 0),(.4,0)] #d2_2
    stimVert5 = [(.2-.2*np.cos(angle*np.pi/180), .2*np.sin(angle*np.pi/180)), (.2, 0), (.2+.4*np.sin(angle*np.pi/180), .4*np.cos(angle*np.pi/180)),(.2, 0),(.2+.2*np.cos(angle*np.pi/180),-.2*np.sin(angle*np.pi/180))]
    if Type=='T':
        return visual.ShapeStim(win, vertices=stimVert1, closeShape=False, lineWidth=lw, pos=pos, ori=0,size=size,autoDraw=True)
        
    if Type=='D1':
        return visual.ShapeStim(win, vertices=stimVert2, closeShape=False, lineWidth=lw, pos=pos, ori=0,size=size,autoDraw=True)

    if Type=='D2_1':
        return visual.ShapeStim(win, vertices=stimVert3, closeShape=False, lineWidth=lw, pos=pos, ori=0,size=size,autoDraw=True)

    if Type=='D2_2':
        return visual.ShapeStim(win, vertices=stimVert4, closeShape=False, lineWidth=lw, pos=pos, ori=0,size=size,autoDraw=True)

    if Type=='30':
        return visual.ShapeStim(win, vertices=stimVert5, closeShape=False, lineWidth=lw, pos=(0,0.8), ori=0,size=size,autoDraw=True)

if __name__ == '__main__':
    #ready=visual.TextStim(win,'ready?', color=(1.0,1.0,1.0),units='norm', height=0.2)
    fixation = visual.TextStim(win, text='+',alignHoriz='center',
                             alignVert='center', units='norm', pos=(0, 0), height=0.2,
                             color=[255, 255, 255], colorSpace='rgb255',wrapWidth=2)
    fixation.setAutoDraw(True)
    thanks=visual.TextStim(win,'thank you for your participation, all tests are concluded',font='Helvetica', alignHoriz='center',
                          alignVert='center', units='norm', height=0.1,color=(1.0,1.0,1.0)) #thank the subject for their participation

    stimTpos1 = list(itertools.product(np.linspace(-0.6,-0.1,num=6),np.linspace(-0.3,0.3,num=6))) #set1
    stimTpos2 = list(itertools.product(abs(np.linspace(-0.6,-0.1,num=6)),np.linspace(-0.3,0.3,num=6))) #set2
    stimTori1 = list(np.linspace(10,30,num=36))
    stimTlist1 = []; stimTlist2 = []

    for n in range((len(stimTpos1)-1)/2):
        stimTlist1.append(make_stim('D1'))
        stimTlist1.append(make_stim('D2_1'))
        stimTlist2.append(make_stim('D1'))
        stimTlist2.append(make_stim('D2_2'))
    stimTlist1.append(make_stim('T'))
    stimTlist2.append(make_stim('T'))
    stimTlist1.append(make_stim('D1'))
    stimTlist2.append(make_stim('D1'))
    shuffle(stimTlist1)
    shuffle(stimTlist2)

    [x.setPos(y) for x,y in zip(stimTlist1,stimTpos1)]
    [x.setPos(y) for x,y in zip(stimTlist2,stimTpos2)]
    for i in range(len(stimTlist1)):
#        stimTlist1[i].pos = stimTpos1[i]
#        stimTlist2[i].pos = stimTpos2[i]
       stimTlist1[i].setOri(stimTori1[i])
       stimTlist1[i].setOri(stimTori1[i])
        
#    stimVertL = np.array([(-.2,-.2),(-.2,.25),(-.15,.25),(-.15,-.15),(.2,-.15),(.2,-.2)])
#    stimL = visual.ShapeStim(win, vertices=stimVert3, 
#                             fillColor='darkgray', lineWidth=0, size=.3, pos=(.2, 0),units='norm')
    #ready.draw()
    a=make_stim('30')
    win.flip()#initialize window 

    
    while not event.getKeys():
        pass
#        try:
##            if stimVert2[0][0]<=stimVert1[0][0]:
##                
##                stimVert2[0][0] = stimVert1[2][0]-0.05
##                stimVert2[1][0] = stimVert1[2][0]-0.05
##                stimVert2[2][0] = stimVert1[2][0]
##                stimVert2[3][0] = stimVert1[2][0]
##            else:
##                stimVert2[0][0] = stimVert2[0][0]-0.003
##                stimVert2[1][0] = stimVert2[1][0]-0.003
##                stimVert2[2][0] = stimVert2[2][0]-0.003
##                stimVert2[3][0] = stimVert2[3][0]-0.003
##            
            
#                stimTlist1[i].vertices = [stimVert1,stimVert2]  # can be slow with many vertices
               
#                stimTlist2[i].draw()
#            #stimL.ori+=1
#            
#           # stimL.draw()
#           
#            win.flip()
#           # core.wait(0.3)
#        except Exception as err:
#            print(err)
#    thanks.draw()
#    win.flip()

    win.close()     #close the psychopy windo
    core.quit()
=======
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:45:48 2017
@author: mz
A test of stimulus similarity
"""

#imports
from psychopy import visual,core,gui,event
from datetime import datetime
import itertools, csv
from random import shuffle
import numpy as np


win = visual.Window([900,900],fullscr=False,allowGUI=True) #psychopy window
c = 0.2 # mean N/T similarity 0< c <0.2
d1=0.2; # D1/T similarity 0< d1 <c
d2 = [2*c-d1,d1-2*c]
p = [abs(d1-d2[0]), abs(d1-d2[1])] # N/N similarity
print('mean N/T similarity: ',c)
print('N/N similarity: ',p)

def make_stim (Type, pos=(0,0),size=0.15, lw=2.5):
    angle =-30
    stimVert1 = [(0, 0), (.2, 0), (.2, .4),(.2, 0),(.4,0)] #target
    stimVert2 = [(0, 0), (.2-d1, 0), (.2-d1, .4),(.2-d1, 0),(.4,0)] #d1
    stimVert3 = [(0, 0), (.2-d2[0], 0), (.2-d2[0], .4),(.2-d2[0], 0),(.4,0)] #d2_1
    stimVert4 = [(0, 0), (.2-d2[1], 0), (.2-d2[1], .4),(.2-d2[1], 0),(.4,0)] #d2_2
    stimVert5 = [(.2-.2*np.cos(angle*np.pi/180), .2*np.sin(angle*np.pi/180)), (.2, 0), (.2+.4*np.sin(angle*np.pi/180), .4*np.cos(angle*np.pi/180)),(.2, 0),(.2+.2*np.cos(angle*np.pi/180),-.2*np.sin(angle*np.pi/180))]
    if Type=='T':
        return visual.ShapeStim(win, vertices=stimVert1, closeShape=False, lineWidth=lw, pos=pos, ori=0,size=size,autoDraw=True)
        
    if Type=='D1':
        return visual.ShapeStim(win, vertices=stimVert2, closeShape=False, lineWidth=lw, pos=pos, ori=0,size=size,autoDraw=True)

    if Type=='D2_1':
        return visual.ShapeStim(win, vertices=stimVert3, closeShape=False, lineWidth=lw, pos=pos, ori=0,size=size,autoDraw=True)

    if Type=='D2_2':
        return visual.ShapeStim(win, vertices=stimVert4, closeShape=False, lineWidth=lw, pos=pos, ori=0,size=size,autoDraw=True)

    if Type=='30':
        return visual.ShapeStim(win, vertices=stimVert5, closeShape=False, lineWidth=lw, pos=(0,0.8), ori=0,size=size,autoDraw=True)

if __name__ == '__main__':
    #ready=visual.TextStim(win,'ready?', color=(1.0,1.0,1.0),units='norm', height=0.2)
    fixation = visual.TextStim(win, text='+',alignHoriz='center',
                             alignVert='center', units='norm', pos=(0, 0), height=0.2,
                             color=[255, 255, 255], colorSpace='rgb255',wrapWidth=2)
    fixation.setAutoDraw(True)
    thanks=visual.TextStim(win,'thank you for your participation, all tests are concluded',font='Helvetica', alignHoriz='center',
                          alignVert='center', units='norm', height=0.1,color=(1.0,1.0,1.0)) #thank the subject for their participation

    stimTpos1 = list(itertools.product(np.linspace(-0.6,-0.1,num=6),np.linspace(-0.3,0.3,num=6))) #set1
    stimTpos2 = list(itertools.product(abs(np.linspace(-0.6,-0.1,num=6)),np.linspace(-0.3,0.3,num=6))) #set2
    stimTori1 = list(np.linspace(10,30,num=36))
    stimTlist1 = []; stimTlist2 = []

    for n in range((len(stimTpos1)-1)/2):
        stimTlist1.append(make_stim('D1'))
        stimTlist1.append(make_stim('D2_1'))
        stimTlist2.append(make_stim('D1'))
        stimTlist2.append(make_stim('D2_2'))
    stimTlist1.append(make_stim('T'))
    stimTlist2.append(make_stim('T'))
    stimTlist1.append(make_stim('D1'))
    stimTlist2.append(make_stim('D1'))
    shuffle(stimTlist1)
    shuffle(stimTlist2)

    [x.setPos(y) for x,y in zip(stimTlist1,stimTpos1)]
    [x.setPos(y) for x,y in zip(stimTlist2,stimTpos2)]
    for i in range(len(stimTlist1)):
#        stimTlist1[i].pos = stimTpos1[i]
#        stimTlist2[i].pos = stimTpos2[i]
       stimTlist1[i].setOri(stimTori1[i])
       stimTlist1[i].setOri(stimTori1[i])
        
#    stimVertL = np.array([(-.2,-.2),(-.2,.25),(-.15,.25),(-.15,-.15),(.2,-.15),(.2,-.2)])
#    stimL = visual.ShapeStim(win, vertices=stimVert3, 
#                             fillColor='darkgray', lineWidth=0, size=.3, pos=(.2, 0),units='norm')
    #ready.draw()
    a=make_stim('30')
    win.flip()#initialize window 

    
    while not event.getKeys():
        pass
#        try:
##            if stimVert2[0][0]<=stimVert1[0][0]:
##                
##                stimVert2[0][0] = stimVert1[2][0]-0.05
##                stimVert2[1][0] = stimVert1[2][0]-0.05
##                stimVert2[2][0] = stimVert1[2][0]
##                stimVert2[3][0] = stimVert1[2][0]
##            else:
##                stimVert2[0][0] = stimVert2[0][0]-0.003
##                stimVert2[1][0] = stimVert2[1][0]-0.003
##                stimVert2[2][0] = stimVert2[2][0]-0.003
##                stimVert2[3][0] = stimVert2[3][0]-0.003
##            
            
#                stimTlist1[i].vertices = [stimVert1,stimVert2]  # can be slow with many vertices
               
#                stimTlist2[i].draw()
#            #stimL.ori+=1
#            
#           # stimL.draw()
#           
#            win.flip()
#           # core.wait(0.3)
#        except Exception as err:
#            print(err)
#    thanks.draw()
#    win.flip()

    win.close()     #close the psychopy windo
    core.quit()
>>>>>>> ed66e39b5913127a1d33244dd06e9832bb258b66
