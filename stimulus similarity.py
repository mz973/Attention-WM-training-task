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

win = visual.Window([1024,768],fullscr=False,allowGUI=True) #psychopy window
c = 0.08 #N/T similarity 0< c <0.2
d1=0.03; #N/N similarity 0< d1 <c
d2 = [c-d1,d1-c]

def make_stim (Type, pos=(0,0)):
    stimVert0 = np.array([(-.2,-.2),(-.2,-.15),(.2,-.15),(.2,-.2)]) #horizontal bar
    stimVert1 = np.array([(-.025,-.15),(-.025,.25),(.025,.25),(.025,-.15)]) #vertical bar target
    stimVert2 =  np.array([(-.025-d1,-.15),(-.025-d1,.25),(.025-d1,.25),(.025-d1,-.15)])#vertical bar D1
    stimVert3 =  np.array([(-.025-d2[0],-.15),(-.025-d2[0],.25),(.025-d2[0],.25),(.025-d2[0],-.15)])#vertical bar D2
    stimVert4 =  np.array([(-.025-d2[1],-.15),(-.025-d2[1],.25),(.025-d2[1],.25),(.025-d2[1],-.15)])#vertical bar D2_2
    if Type=='T':
        return visual.ShapeStim(win, vertices=[stimVert0,stimVert1], 
                                 fillColor='darkgray', lineWidth=0, size=.2,pos=pos, autoDraw=True,units='norm')
    if Type=='D1':
        return visual.ShapeStim(win, vertices=[stimVert0,stimVert2], 
                                 fillColor='darkgray', lineWidth=0, size=.2,pos=pos,autoDraw=True,units='norm')
    if Type=='D2_1':
        return visual.ShapeStim(win, vertices=[stimVert0,stimVert3], 
                                 fillColor='darkgray', lineWidth=0, size=.2,pos=pos,autoDraw=True,units='norm')
    if Type=='D2_2':
        return visual.ShapeStim(win, vertices=[stimVert0,stimVert4], 
                                 fillColor='darkgray', lineWidth=0, size=.2,pos=pos,autoDraw=True,units='norm')

if __name__ == '__main__':
    #ready=visual.TextStim(win,'ready?', color=(1.0,1.0,1.0),units='norm', height=0.2)
    fixation = visual.TextStim(win, text='+',alignHoriz='center',
                             alignVert='center', units='norm', pos=(0, 0), height=0.2,
                             color=[255, 255, 255], colorSpace='rgb255',wrapWidth=2)
    fixation.setAutoDraw(True)
    thanks=visual.TextStim(win,'thank you for your participation, all tests are concluded',font='Helvetica', alignHoriz='center',
                          alignVert='center', units='norm', height=0.1,color=(1.0,1.0,1.0)) #thank the subject for their participation

    stimTpos1 = list(itertools.product([-.6,-.45,-.3,-.15],[-.3,-.15,0.0,.15])) #set1
    stimTpos2 = list(itertools.product([.6,.45,.3,.15],[-.3,-.15,0.0,.15])) #set2

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

    for i in range(len(stimTlist1)):
        stimTlist1[i].pos = stimTpos1[i]
        stimTlist2[i].pos = stimTpos2[i]
        
#    stimVertL = np.array([(-.2,-.2),(-.2,.25),(-.15,.25),(-.15,-.15),(.2,-.15),(.2,-.2)])
#    stimL = visual.ShapeStim(win, vertices=stimVert3, 
#                             fillColor='darkgray', lineWidth=0, size=.3, pos=(.2, 0),units='norm')
    #ready.draw()
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
