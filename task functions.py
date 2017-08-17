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
import itertools, csv, sys, os.path, traceback
from random import shuffle
import numpy as np
from copy import copy
from math import sqrt


class Stimuli:

    def __init__(self, win, timing, orientation):
        self.win = win
        self.timing = timing
        self.orientation=orientation
        self.ready = visual.TextStim(win,'ready?', color=(1.0,1.0,1.0),units='norm', height=0.08, pos=(0,0),wrapWidth=1)
        self.sure = visual.TextStim(win,'Are you sure? Press Escape to exit, press Enter to resume experiment.',
                                        color=(1.0,1.0,1.0),units='norm', height=0.07, pos=(0,0),wrapWidth=2)
        
        self.fixation = visual.TextStim(self.win, text='+',
                                        alignHoriz='center',
                                        alignVert='center', units='norm',
                                        pos=(0, 0), height=0.1,
                                        color=[255, 255, 255], colorSpace='rgb255',
                                        wrapWidth=3)
        self.probe = visual.TextStim(self.win,text='anticlockwise or clockwise?',
                                     font='Helvetica', alignHoriz='center', alignVert='center',
                                     units='norm',pos=(0, 0.8), height=0.08,
                                     color=[255, 255, 255], colorSpace='rgb255',wrapWidth=3)
        self.probe_vs = visual.TextStim(self.win,text='target present or not?',
                                     font='Helvetica', alignHoriz='center', alignVert='center',
                                     units='norm',pos=(0, 0.8), height=0.08,
                                     color=[255, 255, 255], colorSpace='rgb255',wrapWidth=3)
        self.recall_keymap = {'z': 'anticlockwise', 'm': 'clockwise'}
        self.vs_keymap = {'z': 'yes', 'm': 'no'}
        
    def set_ori(self,obj, angle):
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
    def make_stim (self, c, d1, Type,size=0.2, lw=1.5, ori=0, sign=None ):  
        D2 = [2*c-d1,d1-2*c] #calculate d2/T similarity based on c and d1; 
        d2 = [x*0.8 for x in D2] #d2 is composed by 20% orientation and 80% position difference
        if sign is not None:
            d2_ori = sign *abs(D2[0])*0.2/0.2*180  #normalized difference to converge orientation and position
        else:
            d2_ori = ori
        vertice = []
        vertice.append([(0, 0), (.2, 0), (.2, .4),(.2, 0),(.4,0)]) #bar length is 0.4
        vertice.append([(0, 0), (.2-d1, 0), (.2-d1, .4),(.2-d1, 0),(.4,0)])
        vertice.append([(0, 0), (.2-d2[0], 0), (.2-d2[0], .4),(.2-d2[0], 0),(.4,0)]) 
        vertice.append([(0, 0), (.2-d2[1], 0), (.2-d2[1], .4),(.2-d2[1], 0),(.4,0)])
        if Type=='t':#target stimuli
            self.target = visual.ShapeStim(self.win, vertices=vertice[0],
                                 closeShape=False, lineWidth=lw, 
                                 ori=ori,size=size,pos=(0,0),name='target',autoDraw=False)
            return self.target
        if Type=='d1':#distractor 1
            return visual.ShapeStim(self.win, vertices=vertice[1],
                                 closeShape=False, lineWidth=lw, 
                                 ori=ori,size=size,pos=(0,0),name='d1',autoDraw=False)
            
        if Type=='d2_1': #distracor 2-1
            return visual.ShapeStim(self.win, vertices=vertice[2],
                                 closeShape=False, lineWidth=lw, 
                                 ori=d2_ori,size=size,pos=(0,0),name='d2_1',autoDraw=False)
        if Type=='d2_2': #distractor 2-2
            return visual.ShapeStim(self.win, vertices=vertice[3],
                                 closeShape=False, lineWidth=lw, 
                                 ori=d2_ori,size=size,pos=(0,0),name='d2_2',autoDraw=False)
 

    #adjust distractor difficulty and draw search array 
    def search_array(self, trial, condition, target=None, ori=0,setSize=6):#trial contains [c, d1, ori, hard or easy(d1 or d2)]
        self.draw_fixation()
        draw_objs = [] 
        stimpos = list(itertools.product(np.linspace(-0.25*setSize/2,0.25*setSize/2,num=setSize),np.linspace(-0.25*setSize/2,0.25*setSize/2,num=setSize))) #set1
        orilist = [-50,-25,0,25,50]#25 degree step, ramdomize memory array orientations
        stimori = np.random.choice(orilist)#randomly rotate the whole array
        
        #map(lambda x:x*10,stimori)
    
        if condition=='memory':#any stimulus could be probed in recall
            while len(draw_objs)<int(len(stimpos)/2)*2:
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=np.random.choice(orilist)))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type=trial['level'],ori=np.random.choice(orilist)))
            if len(draw_objs)<len(stimpos):
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=np.random.choice(orilist)))
            targetobj = draw_objs[np.random.choice(range(len(stimpos)))]
            
        if condition=='vs': #half of trials have no target
            sign=np.random.choice([-1,1])
            for n in range((len(stimpos)-1)/2):    
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=ori))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type=trial['level'],ori=ori,sign=sign ))
            if target==1:
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='t',ori=ori))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=ori))
                answer='yes'
            if target==0:
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=ori))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type=trial['level'],ori=ori,sign=sign))
                answer= 'no'
                
            [x.setOri(stimori+x.ori)  for x in draw_objs ]
        
        shuffle(draw_objs)
        [x.setPos(y) for x,y in zip(draw_objs,stimpos)]
        
        
        
        D2 = [2*trial['c']-trial['d1'],trial['d1']-2*trial['c']]#calculate NN similarity
        d2 = [x*0.8 for x in D2]  #d2 is composed by 20% orientation and 80% position difference
        
        if trial['level'] =='d2_1':
            p = abs(trial['d1']-d2[0])+0.2*abs(D2[0]) #NN similarity includes orientation and position difference
        else:
            p= abs(trial['d1']-d2[1])+0.2*abs(D2[0])
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
                    return targetobj,p

            return targetobj, p
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
                    return ('NA', answer, resp_time-start_time, p)
            else:
                return (self.vs_keymap[key], answer, resp_time-start_time, p)#return response, correct answer &RT
            
        #draw the rotated target and ask for a binary response
    def recall(self, target, orientation, p):
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
            return ('timeout', answer, resp_time-start_time,p)
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
            return (self.recall_keymap[key], answer, resp_time-start_time, p)#return response, correct answer &RT

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
                                       pos=(0,-0.8), height=0.08,
                                       color=[255, 255, 255], colorSpace='rgb255',
                                       wrapWidth=3)
                                
        if image is not None:
            display_image = visual.ImageStim(win,image='cryingface.jpg',pos=(0.3,-0.8), size=0.1,units='norm')
            display_image.draw()
        display_text.draw()
        self.win.flip()
        key = event.waitKeys(maxWait=max_wait)
        if key is not None:
            if key[0] == 'escape':
                print('quiting experiment')
                raise Exception('quiting')
        self.win.flip()

def stimulirule(triallist):#get rid of trial types (d1,d2,c) that do not conform to set rules
    trial_list=[]
    for i, trial in enumerate(triallist):
        if trial['level'] =='d2_1':
            d2 = (2*trial['c']-trial['d1'])*0.8
        else:
            d2= (trial['d1']-2*trial['c'])*0.8
        if trial['d1']<0.2 and trial['d1']>0.1 and abs(d2)<0.2 and abs(d2)>0.1 and trial['d1']!=d2:
            
            trial_list.append(trial)
    return trial_list

def blockbreak(win, num):#create a break in between trials and present progress message
    msg1 = visual.TextStim(win,'Well done!',color=(1.0,1.0,1.0),units='norm', height=0.07, pos=(0,0.1),wrapWidth=1)
    msg2 = visual.TextStim(win,str(num)+'/4 block completed',color=(1.0,1.0,1.0),units='norm', height=0.07, pos=(0,0),wrapWidth=2)
    msg3 = visual.TextStim(win,'Press Enter to continue',color=(1.0,1.0,1.0),units='norm', height=0.07, pos=(0,-0.1),wrapWidth=2)
    msg1.draw()
    msg2.draw()
    msg3.draw()
    win.flip()
    event.waitKeys(maxWait=float('inf'), keyList=['return'],timeStamped=False)
    win.flip()

def get_window():
    return visual.Window([800,800],
        winType='pyglet', monitor="testMonitor",fullscr=False, colorSpace='rgb',color=(-1,-1,-1),units='norm')

def autoDraw_on(stim):
    stim.autoDraw = True
    return stim

def autoDraw_off(stim):
    stim.autoDraw = False
    return stim

#ideally this function takes 2 similarity index directly 
#and generate eligible trials.
def trialGen(c,p): #c is NT similarity, p is NN similarity
    import warnings, random
    #0<c<2; d1,d2<2 
    P=[]
    if p>2*c or p>(4-2*c) or p>2*c-1 or c>2:
        warnings.warn('c or p is not in acceptable range')
        return [0]
    else:
        d1= c-p/2; d2 = c+p/2
        #d1= c+p/2; d2 = c-p/2
        if d1<=1: 
            x1 = round(random.uniform(0.5,d1),2) #make sure x1(bar position) is far enough from target
        else:  
            x1 = round(random.uniform(0.5,1),2) 
        y1 = d1-x1
        if d2<=1: 
            x2_1 = np.linspace(0.5,d2,11)
            x2_2 = -1 * x2_1
        else:  
            x2_1 = np.linspace(0.5,1,11) #round(random.uniform(0.5,1),2) * 1
            x2_2 = -1 * x2_1
        y2_1 = d2 - (x2_1)
        y2_2 = -1 * y2_1
        for i in range(len(x2_1)):
            temp = [abs(x1-x2_1[i])+abs(y1-y2_1[i]),abs(x1-x2_1[i])+abs(y1-y2_2[i]),abs(x1-x2_2[i])+abs(y1-y2_1[i]),abs(x1-x2_2[i])+abs(y1-y2_2[i])]
            P.extend(temp)
        P = [round(x,2) for x in P]
        P = np.unique(P)
        P.sort()
        return P
        print (P,'\n',(d1+d2)/2)

        
        #need some kind of screening rule and a while loop
        

def run_vs(win, fi=None,setSize=4):
#    (expname, sid, numblocks, speed, mark_mode, input_mode) = get_settings()
    win.flip()
    timing = {'fixation': 0.8, #set timing
              'search': float('inf'),
              'blank': 2,
              'recall': 4 ,
              'intertrial': 1.0}
#
    orientation = [0]
    constant = list(np.arange(0.08,0.25,0.02)) #set N/T similarity, step is .02
    d1=[] #set D1/T similarity
    for i in range(len(constant)):
        a=list(np.arange(0.1,0.2,0.01)) #step is .01
        d1.append([x for x in a if x<0.2])
    
    stim = Stimuli(win, timing, orientation)

    stim.text_and_stim_keypress('Welcome to the attention and working memory study',pos=(0,0.7),
                                stim=stim.ready)
    stim.text_and_stim_keypress('This is a visual search task',pos=(0,0.7),
                                stim=stim.fixation)

    trial_type=[]
    for i in range(len(constant)):
        trial_type =trial_type+ list(itertools.product([constant[i]],d1[i],orientation))
    trial_list=[]
    for i in range(len(trial_type)):
        trial = {}
        trial['c'] = trial_type[i][0]
        trial['d1'] = trial_type[i][1]
        trial['ori'] = trial_type[i][2]
        trial['level'] = 'd2_2'
        trial_list.append(trial)
    for i in range(len(trial_type)):
        trial = {}
        trial['c'] = trial_type[i][0]
        trial['d1'] = trial_type[i][1]
        trial['ori'] = trial_type[i][2]
        trial['level'] = 'd2_1'
        trial_list.append(trial)
        
    triallist = stimulirule(trial_list) #get rid of trials that do not conform to selection rules
    trial_list=[]
    for i,trial in enumerate(triallist): #half trials have target, half do not
        trial['target']=1
        trial_list.append(copy(trial))
    for i,trial in enumerate(triallist): #half trials have target, half do not
        trial['target']=0
        trial_list.append(copy(trial))
    
    trial_list=trial_list*4 #inclement trial numbers
    shuffle(trial_list)
    print (len(trial_list))
    # run trials
    for i, trial in enumerate(trial_list):
        try:
            resp, answer, rt, NN = stim.search_array(trial,condition='vs',target= trial['target'],setSize=setSize)
            corr = (resp == answer)
            if not corr:
                if resp == 'timeout':
                    stim.text('Timeout',max_wait=0.6)
                else:
                    stim.text('Incorrect',image=1, max_wait=0.6)
                   # condition', 'answer', 'response', 'RT', 'N/T similarity','N/N similarity','orientation'
            
            if fi is not None:
                fi.writerow(['%s, %s, %s, %.3f, %.2f, %.2f, %d'%('vs', answer, resp, rt*1000, trial['c'], NN, 0)])
            if i!=0 and i%(int(len(trial_list)/4))==0:
                blockbreak(win, i/int((len(trial_list)/4)))
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
#    (expname, sid, numblocks, speed, mark_mode, input_mode) = get_settings()
    
    win.flip()
    timing = {'fixation': 0.8,
              'search': 6, #float('inf'),
              'blank': 2,
              'recall': 6 ,
              'intertrial': 1.0}
#
    orientation = [-50,-25,25,50] #staircase #as used in Bayes(2008)
    constant = [0.15] #Aaverage of vs condition
    d1=[0.15]

    stim = Stimuli(win, timing, orientation)

    stim.text_and_stim_keypress('Welcome to the attention and working memory study',pos=(0,0.7),
                                stim=stim.ready)
    stim.text_and_stim_keypress('This is a memory task',pos=(0,0.7),
                                stim=stim.fixation)

    # construct blocks
#    for block_num in range(numblocks):
#        block = {}
#        block['speed_factor'] = speed
#        block['block_num'] = block_num
#        block['cue_color'] = random.choice(colors.keys())
#        random.shuffle(trial_types)
#        trial_list = []
    # construct trials
    trial_type=[]
    trial_type =trial_type+ list(itertools.product(constant,d1,orientation))
    trial_list=[]
    for i in range(len(trial_type)):
        trial = {}
        trial['c'] = trial_type[i][0]
        trial['d1'] = trial_type[i][1]
        trial['ori'] = trial_type[i][2]
        trial['level'] = 'd2_2'
        trial_list.append(trial)

    trial_list=trial_list*8 #inclement trial numbers

    shuffle(trial_list)
    print (len(trial_list))
    # run trials
    for i, trial in enumerate(trial_list):
        try:
            target, p = stim.search_array(trial,condition='memory',setSize=setSize)
            resp, answer, rt, NN = stim.recall(target=target, orientation=trial['ori'], p=p)
            corr = (resp == answer)
            if not corr:
                if resp == 'timeout':
                    stim.text('Timeout',max_wait=0.6)
                else:
                    stim.text('Incorrect',max_wait=0.6)  
            if fi is not None:
                fi.writerow(['%s, %s, %s, %.3f, %.2f, %.2f, %d'%('memory', answer, resp, rt*1000, trial['c'], NN, trial['ori'])])
            if i!=0 and i%(int(len(trial_list)/4))==0:
                blockbreak(win, i/int((len(trial_list)/4)))
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
        outWr.writerow(['%s, %s, %s, %s, %s,%s, %s'%('condition', 'answer', 'response', 'RT', 'N/T similarity','N/N similarity','orientation')]) # write out header
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
    print "all tests concluded"    



if __name__ == '__main__':
    filewriter, fname , condition = get_settings()
    win = get_window()
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