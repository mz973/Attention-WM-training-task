#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:45:48 2017
@author: mz
to-do:
    
    staircase implementation
"""

#imports
from psychopy import visual,core,gui,event
from datetime import datetime
import itertools, csv, traceback
from random import shuffle
import numpy as np
from copy import copy
from math import sqrt


class Stimuli:

    def __init__(self, win, timing):
        self.win = win
        self.timing = timing

        self.ready = visual.TextStim(win,'Ready?', color=(1.0,1.0,1.0),units='norm', height=0.08, pos=(0,0),wrapWidth=1)
        self.sure = visual.TextStim(win,'Are you sure? Press Escape to exit, press Enter to resume experiment.',
                                        color=(1.0,1.0,1.0),units='norm', height=0.07, pos=(0,0),wrapWidth=2)
        
        self.fixation = visual.TextStim(self.win, text='+',
                                        alignHoriz='center',
                                        alignVert='center', units='norm',
                                        pos=(0, 0), height=0.1,
                                        color=[255, 255, 255], colorSpace='rgb255',
                                        wrapWidth=3)
        self.probe = visual.TextStim(self.win,text='z: anticlockwise   m: clockwise',
                                     font='Helvetica', alignHoriz='center', alignVert='center',
                                     units='norm',pos=(0, 0.8), height=0.08,
                                     color=[255, 255, 255], colorSpace='rgb255',wrapWidth=4)
        self.probe_vs = visual.TextStim(self.win,text='z: target present   m: target not present',
                                     font='Helvetica', alignHoriz='center', alignVert='center',
                                     units='norm',pos=(0, 0.8), height=0.08,
                                     color=[255, 255, 255], colorSpace='rgb255',wrapWidth=4)
        self.recall_keymap = {'z': 'anticlockwise', 'm': 'clockwise'}
        self.vs_keymap = {'z': 'yes', 'm': 'no'}
        
    def set_ori(self,obj, angle):#depricated
        an = angle*np.pi/180
        vertice = obj.vertices
        x = vertice[1][0]
        beta = an-np.arctan((.2-x)/.4)
        vertice = [(.2-.2*np.cos(an), .2*np.sin(an)), (.2-np.cos(an)*(.2-x), np.sin(an)*(.2-x)), (.2+sqrt(.4**2+(.2-x)**2)*np.sin(beta), sqrt(.4**2+(.2-x)**2)*np.cos(beta)), (.2-np.cos(an)*(.2-x), np.sin(an)*(.2-x)),(.2+.2*np.cos(an),-.2*np.sin(an))]
        obj.setVertices(vertice)
        
        
    def get_input(self, max_wait=3.0, keylist=None):

        key = event.waitKeys(maxWait=max_wait, keyList=keylist,timeStamped=True)
        if key is not None:
            key = key[0][0]
        time = core.getTime()

        return (key, time)

    def draw_fixation(self):
    
        self.fixation.draw()
        self.win.flip()
        core.wait(self.timing['fixation'])
        self.win.flip()

#        c  mean N/T similarity 0< c <0.2
#        d1# D1/T similarity 0< d1 <c
    def make_stim (self, x, y, target=0,size=0.2, lw=1.5 ):  
        bar_length = 0.25
        d1 = x*bar_length/2
        vertice = [(0, 0), (bar_length/2-d1, 0), (bar_length/2-d1, bar_length),(bar_length/2-d1, 0),(bar_length,0)] #bar length 
        
        return visual.ShapeStim(self.win, vertices=vertice,
                                closeShape=False, lineWidth=lw, 
                                ori=y*180,size=size,pos=(0,0),name='stimuli',autoDraw=False)
 

    #adjust distractor difficulty and draw search array 
    def search_array(self, trial, condition, target=None, ori=0,setSize=4):#trial contains [c, d1, ori, hard or easy(d1 or d2)]
        self.draw_fixation()
        draw_objs = [] ; display_dis = 0.15
        
        stimpos = list(itertools.product(np.linspace(-display_dis*setSize/2,display_dis*setSize/2,num=setSize),
                                         np.linspace(-display_dis*setSize/2,display_dis*setSize/2,num=setSize))) #set1
        orilist = [-25,-5,0,5,25]#25 degree step, ramdomize memory array orientations
        stimori = np.random.choice(orilist)#randomly rotate the whole array
        
        #map(lambda x:x*10,stimori)
    
        if condition=='memory':#any stimulus could be probed in recall
            while len(draw_objs)<int(len(stimpos)/2)*2:
                draw_objs.append(self.make_stim(x=trial['x1'],y=np.random.choice(orilist)/180.0))#distractor1
                draw_objs.append(self.make_stim(x=trial['x2'],y=np.random.choice(orilist)/180.0))#distractor2
            if len(draw_objs)<len(stimpos):
                draw_objs.append(self.make_stim(x=trial['x2'],y=np.random.choice(orilist)/180.0))
            targetobj = draw_objs[np.random.choice(range(len(stimpos)))]
            
            
            
        if condition=='vs': #half of trials have no target
            
            for n in range((setSize**2-1)/2):    
                draw_objs.append(self.make_stim(x=trial['x1'],y=trial['y1']))#distractor1
                draw_objs.append(self.make_stim(x=trial['x2'],y=trial['y2']))#distractor2
            if target==1:
                draw_objs.append(self.make_stim(x=0,y=0))#target
                answer='yes'
            else: answer= 'no'
            while len(draw_objs)<setSize**2:
                draw_objs.append(self.make_stim(x=trial['x2'],y=trial['y2']))

                
                
            [x.setOri(stimori+x.ori)  for x in draw_objs ]
        
        shuffle(draw_objs)
        [x.setPos(y) for x,y in zip(draw_objs,stimpos)]
        
        
        #NN = visual.TextStim(self.win,p, color=(1.0,1.0,1.0),units='norm', height=0.05, pos=(0,-0.8))
        #NN.draw()
        
        map(autoDraw_on, draw_objs)
        if condition=='vs':
            self.probe_vs.draw()
        start_time = self.win.flip()
        if condition=='memory':
            key, resp_time = self.get_input(max_wait=self.timing['search'],
                                            keylist= ['escape'])
            map(autoDraw_off, draw_objs)
            self.win.flip()
            if key is None:
                pass
            else:
                self.sure.draw()
                self.win.flip()
                k, r =self.get_input(max_wait=float('inf'),keylist=['escape','return'])
                if k=='escape':
                    
                    print('quiting experiment')
                    raise Exception('quiting')
                else:
                    pass
            
            #delay blank screen
            key, resp_time = self.get_input(max_wait=self.timing['blank'],
                                            keylist=['escape'])
            if key is None:
                pass
            else:
                self.sure.draw()
                self.win.flip()
                k, r =self.get_input(max_wait=float('inf'),keylist=['escape','return'])
                if k=='escape':
                    print('quiting experiment')
                    raise Exception('quiting')
                else:
                    return targetobj

            return targetobj
        if condition=='vs':
            key, resp_time = self.get_input(max_wait=self.timing['search'],
                                        keylist=self.recall_keymap.keys() + ['escape'])
            map(autoDraw_off, draw_objs)  
            self.win.flip()
            if key is None:
                return ('timeout', answer, resp_time-start_time,p)
            elif key == 'escape':
                self.sure.draw()
                self.win.flip()
                k, r =self.get_input(max_wait=float('inf'),keylist=['escape','return'])
                if k=='escape':
                    print('quiting experiment')
                    raise Exception('quiting')
                else:
                    return ('NA', answer, resp_time-start_time)
            else:
                return (self.vs_keymap[key], answer, resp_time-start_time)#return response, correct answer &RT
            
        #draw the rotated target and ask for a binary response
    def recall(self, target, orientation):
        target_probe = copy(target)
        an = target_probe.ori
        
        self.set_ori(target_probe,orientation+an)
        if orientation >=0:
            answer = 'clockwise'
        else:
            answer = 'anticlockwise'
        target_probe.draw()
        self.probe.draw()
        start_time = self.win.flip()
        key, resp_time = self.get_input(max_wait=self.timing['recall'],
                                        keylist=self.recall_keymap.keys() + ['escape'])
        self.win.flip()
        if key is None:
            return ('timeout', answer, resp_time-start_time)
        elif key == 'escape':
                self.sure.draw()
                self.win.flip()
                k, r =self.get_input(max_wait=float('inf'),keylist=['escape','return'])
                if k=='escape':
                    print('quiting experiment')
                    raise Exception('quiting')
                else:
                    pass
        else:
            return (self.recall_keymap[key], answer, resp_time-start_time)#return response, correct answer &RT

    def text_and_stim_keypress(self, text, stim=None,pos=(0,-0.8), max_wait=float('inf')):
        if stim is not None:
            if type(stim) == list:
                map(lambda x: x.draw(), stim)
            else:
                stim.draw()
        display_text = visual.TextStim(self.win, text=text,
                                       font='Helvetica', alignHoriz='center',
                                       alignVert='center', units='norm',
                                       pos=pos, height=0.08,
                                       color=[255, 255, 255], colorSpace='rgb255',
                                       wrapWidth=3)
        display_text.draw()
        self.win.flip()
        key = event.waitKeys(maxWait=max_wait)
        if key is not None:
            if key[0] == 'escape':
                print('quiting experiment')
                raise Exception('quiting')
        self.win.flip()

    def text(self,text,image=None, max_wait=3.0):
        display_text = visual.TextStim(self.win, text=text,
                                       font='Helvetica', alignHoriz='center',
                                       alignVert='center', units='norm',
                                       pos=(0,0), height=0.1,
                                       color=[255, 255, 255], colorSpace='rgb255',
                                       wrapWidth=3)
                                
        if image is not None:
            display_image = visual.ImageStim(win,image='cryingface.jpg',pos=(0.22,0), size=0.08,units='norm')
            display_image.draw()
        display_text.draw()
        self.win.flip()
        key = event.waitKeys(maxWait=max_wait)
        if key is not None:
            if key[0] == 'escape':
                print('quiting experiment')
                raise Exception('quiting')
        self.win.flip()


def blockbreak(win, num, total):#create a break in between trials and present progress message
    msg1 = visual.TextStim(win,'Well done!',color=(1.0,1.0,1.0),units='height', height=0.07, pos=(0,0.1),wrapWidth=1)
    msg2 = visual.TextStim(win,str(num)+'/%d block completed'%(total),color=(1.0,1.0,1.0),units='norm', height=0.07, pos=(0,0),wrapWidth=2)
    msg3 = visual.TextStim(win,'Press Return to continue',color=(1.0,1.0,1.0),units='norm', height=0.07, pos=(0,-0.1),wrapWidth=2)
    msg1.draw()
    msg2.draw()
    msg3.draw()
    win.flip()
    event.waitKeys(maxWait=float('inf'), keyList=['return'],timeStamped=False)
    win.flip()

def get_window(width):
    return visual.Window([width,width],
        winType='pyglet', monitor="testMonitor",fullscr=True, colorSpace='rgb',color=(-1,-1,-1),units='height')

def autoDraw_on(stim):
    stim.autoDraw = True
    return stim

def autoDraw_off(stim):
    stim.autoDraw = False
    return stim

#to be used after trialGen, not use it after trialGen_ori
def stimulirule(parameter, yrule):#parameters format: x1 y1 x2 y2, yrule to control orientation to be <90 degree
    triallist=[]; P = []
    for i in range(parameter.shape[0]):
        if abs(parameter[i,1]) <= yrule and abs(parameter[i,3])<=yrule and parameter[i,0]!=parameter[i,2]:
            triallist.append(parameter[i,:])
            P.extend([abs(parameter[i,0]-parameter[i,2])+abs(parameter[i,1]-parameter[i,3])])
            P = [round(x,2) for x in P]
    P,indice = np.unique(P,return_index=True)
    triallist = np.array(triallist)[indice]
    return P, np.array(triallist)

#ideally this function takes 2 similarity index directly 
#and generate eligible trials.
# add rules:
    #x1 x2 should not be same
    #y1 y2 in range (0, 0.5)
"""
depricated in this version of script, using trialGen_ori instead
"""
def trialGen(c,p): #c is NT disimilarity, p is NN disimilarity    #0<c<2; 0<p<4, d1,d2<2 
    import warnings
    P=[]; triallist=[] #triallist: x1, y1,x2,y2
    if p>2*c or p>(4-2*c) or p>2*c-1 or c>2:
        warnings.warn('c or p is not in acceptable range')
        return [0]
    else:
        d1= c-p/2; d2 = c+p/2
        #d1= c+p/2; d2 = c-p/2
        if d1<=1: 
            x1 = np.arange(0.5,d1,0.05)#make sure x1(bar position) is far enough from target
             
        else:  
            x1 = np.arange(0.5,1,0.05)
        y1 = d1-x1
        
        if d2<=1: 
            x2_1 = np.arange(0.5,d2,0.05)
            x2_2 = -1 * x2_1
        else:  
            x2_1 = np.arange(0.5,1,0.05) #round(random.uniform(0.5,1),2) * 1
            x2_2 = -1 * x2_1
        y2_1 = d2 - (x2_1)
        y2_2 = -1 * y2_1
        for x,y in zip(x1,y1):
            for i in range(len(x2_1)):
                temp = [abs(x-x2_1[i])+abs(y-y2_1[i]),abs(x-x2_1[i])+abs(y-y2_2[i]),abs(x-x2_2[i])+abs(y-y2_1[i]),abs(x-x2_2[i])+abs(y-y2_2[i])]
                P.extend(temp)
                triallist.append([x,y,x2_1[i],y2_1[i]])
                triallist.append([x,y,x2_1[i],y2_2[i]])
                triallist.append([x,y,x2_2[i],y2_1[i]])
                triallist.append([x,y,x2_2[i],y2_2[i]])
        P = [round(x,2) for x in P]
        P,indice = np.unique(P,return_index=True)
        #P.sort()
        triallist = np.array(triallist)
   #     triallist = triallist[indice]
        return P, indice, triallist
        

#c is constant, c=|y1|+|y2|
#randomize bar position, one orientation difference value can have multiple composition
def trialGen_ori(c,limit, step):   #randomize bar position   #0<c<2; d2 <1 (max is 180 degree), limit is the max orientation a distractor has
    triallist=[] #triallist: x1, y1,x2,y2
    p = []; C=[]
    d2 = np.arange(0,limit,step) #only works when c > max(d2)
    for y in d2:
        y1 = np.array([(-1*c-y)/2,(c-y)/2, round(np.random.uniform(-0.4,0.4),2),round(np.random.uniform(-0.4,0.4),2)]) #first 2 elements allows the same c, 3rd one doesn't
        y2 = y1+y
        x1 = np.round(np.random.uniform(0.5,0.7,4),1) #bar position is jittered but always >0.5
        x2 = np.round(np.random.uniform(0.5,0.7,4),1)  * np.array([-1,-1,-1,-1])
        for each in zip(x1,y1,x2,y2):
            triallist.append(each)
            p.append(abs(each[1]-each[3]))
            C.append(abs(each[1])+abs(each[3]))
    triallist = np.array(triallist)
    return np.round(C,1), np.round(p,2), triallist


def run_vs(win, fi=None,setSize=3):
#    (expname, sid, numblocks, speed, mark_mode, input_mode) = get_settings()
    win.flip()
    timing = {'fixation': 0.8, #set timing
              'search': float('inf'),
              'blank': 2,
              'recall': 4 ,
              'intertrial': 1.0}

    stim = Stimuli(win, timing)

    stim.text_and_stim_keypress('Welcome to the attention and working memory study',pos=(0,0.7),
                                stim=stim.ready)
    stim.text_and_stim_keypress('This is a visual search task',pos=(0,0.7),
                                stim=stim.fixation)

#    a,b,c = trialGen(1,0.1)
#    p, parameters = stimulirule(c,0.45) #0.5 = +/- 90 degree
    c, p, parameters = trialGen_ori(0.7, 0.7, 0.1) #c is mean NT disimilarity(only y), p is NN(only y), parameters has x1,y1,x2,y2
    triallist=[]
    for i in range(len(parameters)):
        trial = {}
        trial['x1'] =parameters[i][0]
        trial['y1'] = parameters[i][1]
        trial['x2'] = parameters[i][2]
        trial['y2'] = parameters[i][3]
        trial['p'] = p[i]
        trial['c'] = c[i]
        triallist.append(trial)
    trial_list = []
    for i,trial in enumerate(triallist): #half trials have target, half do not
        trial['target']=1
        trial_list.append(copy(trial))
    for i,trial in enumerate(triallist): #half trials have target, half do not
        trial['target']=0
        trial_list.append(copy(trial))
    
    trial_list=trial_list*5 #inclement trial numbers
    shuffle(trial_list)
    print (len(trial_list))
    # run trials
    for i, trial in enumerate(trial_list):
        try:
            resp, answer, rt = stim.search_array(trial,condition='vs',target= trial['target'],setSize=setSize)
            corr = (resp == answer)
            if not corr:
                if resp == 'timeout':
                    stim.text('Timeout',max_wait=0.6)
                else:
                    stim.text('Incorrect',image=1, max_wait=0.6)
                   # condition', 'answer', 'response', 'RT', 'N/T similarity','N/N similarity','orientation'
            
            if fi is not None:
                fi.writerow(['%s, %s, %s, %d, %.3f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %d'%('vs', answer, resp, int(corr), rt*1000, 
                                trial['c'], trial['p'], trial['x1'],trial['y1'],trial['x2'],trial['y2'],0)])
            if i!=0 and i%(int(len(trial_list)/4))==0:
                blockbreak(win, i/int((len(trial_list)/4)), 4)
            core.wait(timing['intertrial'])
        except Exception as err:
            if err =='quiting':
                raise Exception('quiting')
            else:
                traceback.print_exc()
                raise Exception(err)
      
            
    stim.text_and_stim_keypress('Congratulations! You have finished.',
                                        max_wait=2.0)


def run_memory(win,fi, setSize=3):
    
    win.flip()
    timing = {'fixation': 0.8,
              'search': 6, #float('inf'),
              'blank': 2,
              'recall': 6 ,
              'intertrial': 1.0}
##
    

    stim = Stimuli(win, timing)

    stim.text_and_stim_keypress('Welcome to the attention and working memory study',pos=(0,0.7),
                                stim=stim.ready)
    stim.text_and_stim_keypress('This is a memory task',pos=(0,0.7),
                                stim=stim.fixation)

    # construct trials
    orientation = [-50,-25,-5,5,25,50] #staircase #as used in Bayes(2008)
    triallist=[]
    for i in range(len(orientation)):
        trial = {}
        trial['x1'] =0.5
        trial['y1'] = 0
        trial['x2'] = -0.5
        trial['y2'] = 0
        trial['p'] = 1
        trial['c'] = 1
        trial['ori'] = orientation[i]
        triallist.append(trial)

    triallist=triallist*8 #inclement trial numbers

    shuffle(triallist)
    print (len(triallist))
    # run trials
    for i, trial in enumerate(triallist):
        try:
            target = stim.search_array(trial,condition='memory',setSize=setSize)
            resp, answer, rt = stim.recall(target=target, orientation=trial['ori'])
            corr = (resp == answer)
            if not corr:
                if resp == 'timeout':
                    stim.text('Timeout',max_wait=0.6)
                else:
                    stim.text('Incorrect',max_wait=0.6)  
            if fi is not None:
                fi.writerow(['%s, %s, %s, %d,%.3f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %d'%('vs', answer, resp, int(corr), rt*1000, 
                                trial['c'], trial['p'], trial['x1'],trial['y1'],trial['x2'],trial['y2'],trial['ori'])])
            if i!=0 and i%(int(len(triallist)/2))==0:
                blockbreak(win, i/int((len(triallist)/2)), 2)
            core.wait(timing['intertrial'])
        except Exception as err:
            if err =='quiting':
                raise Exception('quiting')
            else:
                traceback.print_exc()
                raise Exception(err)
            
        
    stim.text_and_stim_keypress('Congratulations! You have finished.',
                                        max_wait=2.0)


def get_settings():
    data={}
    data['expname']='Attention_WM'
    data['expdate']=datetime.now().strftime('%Y%m%d_%H%M')
    data['PID']=''
    data['condition']=['vs','memory']
    data['create file'] = False
    dlg=gui.DlgFromDict(data,title='Exp Info',fixed=['expname','expdate'],order=['expname','expdate','PID','condition','create file'])

    if not dlg.OK:
        core.quit()
    if data['create file']==True:
        outName='P%s_%s_%s.csv'%(data['PID'],data['condition'],data['expdate'])
        outFile = open(outName, 'wb')
        outWr = csv.writer(outFile, delimiter=';', lineterminator='\n', quotechar=' ', quoting=csv.QUOTE_MINIMAL) # a .csv file with that name. Could be improved, but gives us some control
        outWr.writerow(['%s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s'%(
                            'condition', 'answer', 'response', 'correct', 'RT', 
                            'N/T disimilarity','N/N disimilarity','x1','y1','x2','y2','orientation')]) # write out header
        return outWr, outFile, data['condition']
    else: 
        return None,None,data['condition']

    #cleanup/file closing/participant thank you messag
def close(win, fname=None):
    if fname is not None:
        fname.close() #close the output file
    thanks = visual.TextStim(win,'Thank you for your participation',font='Helvetica', alignHoriz='center',
                          alignVert='center', units='norm', height=0.1,color=(1.0,1.0,1.0),wrapWidth=3)    
    thanks.draw()
    win.flip()
    event.waitKeys(keyList=['return'])    
    win.close()     #close the psychopy windo
    core.quit()
    print ("all tests concluded")    



if __name__ == '__main__':
    filewriter, fname , condition = get_settings()
    win = get_window(1200)
    if condition=='memory':
        try:
            run_memory(win,filewriter,setSize=3)
        except Exception:        
            close(win,fname=fname)
            
    else:
        try:
            run_vs(win,filewriter)
        except Exception:        
            close(win,fname=fname)