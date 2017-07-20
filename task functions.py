
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:45:48 2017
@author: mz

to-do:
    write to csv
    quit function
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
        self.fixation = visual.TextStim(self.win, text='+',
                                        alignHoriz='center',
                                        alignVert='center', units='norm',
                                        pos=(0, 0), height=0.1,
                                        color=[255, 255, 255], colorSpace='rgb255',
                                        wrapWidth=3)
        self.probe = visual.TextStim(self.win,text='clockwise or anticlockwise?',
                                     font='Helvetica', alignHoriz='center', alignVert='center',
                                     units='norm',pos=(0, 0.8), height=0.08,
                                     color=[255, 255, 255], colorSpace='rgb255',wrapWidth=3)
        self.probe_vs = visual.TextStim(self.win,text='target present or not?',
                                     font='Helvetica', alignHoriz='center', alignVert='center',
                                     units='norm',pos=(0, 0.8), height=0.08,
                                     color=[255, 255, 255], colorSpace='rgb255',wrapWidth=3)
        self.recall_keymap = {'z': 'clockwise', 'm': 'anticlockwise'}
        self.vs_keymap = {'z': 'yes', 'm': 'no'}
#        c  mean N/T similarity 0< c <0.2
#        d1# D1/T similarity 0< d1 <c
    def make_stim (self, c, d1, Type,size=0.2, lw=1.5, ori=0):  
        d2 = [2*c-d1,d1-2*c]
        vertice = []
        vertice.append([(0, 0), (.2, 0), (.2, .4),(.2, 0),(.4,0)])
        vertice.append([(0, 0), (.2-d1, 0), (.2-d1, .4),(.2-d1, 0),(.4,0)])
        vertice.append([(0, 0), (.2-d2[0], 0), (.2-d2[0], .4),(.2-d2[0], 0),(.4,0)]) 
        vertice.append([(0, 0), (.2-d2[1], 0), (.2-d2[1], .4),(.2-d2[1], 0),(.4,0)])
        if Type=='t':
            self.target = visual.ShapeStim(self.win, vertices=vertice[0],
                                 closeShape=False, lineWidth=lw, 
                                 ori=ori,size=size,pos=(0,0),name='target',autoDraw=False)
            return self.target
        if Type=='d1':
            return visual.ShapeStim(self.win, vertices=vertice[1],
                                 closeShape=False, lineWidth=lw, 
                                 ori=ori,size=size,pos=(0,0),name='d1',autoDraw=False)

            
        if Type=='d2_1':
            return visual.ShapeStim(self.win, vertices=vertice[2],
                                 closeShape=False, lineWidth=lw, 
                                 ori=ori,size=size,pos=(0,0),name='d2_1',autoDraw=False)
        if Type=='d2_2':
            return visual.ShapeStim(self.win, vertices=vertice[3],
                                 closeShape=False, lineWidth=lw, 
                                 ori=ori,size=size,pos=(0,0),name='d2_2',autoDraw=False)
 
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

    #adjust distractor difficulty and draw search array 
    def search_array(self, trial, condition, ori=0,setSize=6):#trial contains [c, d1, ori, hard or easy(d1 or d2)]
        self.draw_fixation()
        draw_objs = [] 
        stimpos = list(itertools.product(np.linspace(-0.2*setSize/2,0.2*setSize/2,num=setSize),np.linspace(-0.2*setSize/2,0.2*setSize/2,num=setSize))) #set1

        stimori = np.random.choice([-10,10,-15,15,-20,20,-25,25,-30,30,-35,35],2)#randomly rotate the whole array
        
        #map(lambda x:x*10,stimori)
    
        if condition=='memory':#any stimulus could be probed in recall
            for n in range((len(stimpos)-1)/3):
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=ori))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type=trial['level'],ori=ori))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='t',ori=ori))
            while len(draw_objs)<len(stimpos):
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type=np.random.choice(['d1',trial['level'],'t']),ori=ori))
            target = draw_objs[np.random.choice(range(len(stimpos)))]
        if condition=='vs': #half of trials have no target
            for n in range((len(stimpos)-1)/2):    
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=ori))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type=trial['level'],ori=ori))
            if np.random.choice([0,1])==0:
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='t',ori=ori))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=ori))
                answer='yes'
            else:
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type='d1',ori=ori))
                draw_objs.append(self.make_stim(c=trial['c'], d1=trial['d1'], Type=trial['level'],ori=ori))
                answer= 'no'
        
        shuffle(draw_objs)
        [x.setPos(y) for x,y in zip(draw_objs,stimpos)]
        [x.setOri(stimori[0])  for x in draw_objs if x.name=='target' or x.name=='d1']
        [x.setOri(stimori[1])  for x in draw_objs if x.name=='d2_1' or x.name=='d2_2']
        
        d2 = [2*trial['c']-trial['d1'],trial['d1']-2*trial['c']]
        if trial['level'] =='d2_1':
            p = abs(trial['d1']-d2[0])
        else:
            p= abs(trial['d1']-d2[1])
        NN = visual.TextStim(self.win,p, color=(1.0,1.0,1.0),units='norm', height=0.05, pos=(0,-0.8))
        NN.draw()
        map(autoDraw_on, draw_objs)
        if condition=='vs':
            self.probe_vs.draw()
        start_time = self.win.flip()
        if condition=='memory':
            key, resp_time = self.get_input(max_wait=self.timing['search'],
                                            keylist= ['escape'])
            if key is None:
                pass
            else:
                print('quiting experiment')
                raise Exception('quiting')
            map(autoDraw_off, draw_objs)
            self.win.flip()
            #delay blank screen
            key, resp_time = self.get_input(max_wait=self.timing['blank'],
                                            keylist=['escape'])
            if key is None:
                pass
            else:
                print('quiting experiment')
                raise Exception('quiting')
                
            return target, p
        if condition=='vs':
            key, resp_time = self.get_input(max_wait=self.timing['search'],
                                        keylist=self.recall_keymap.keys() + ['escape'])
            map(autoDraw_off, draw_objs)  
            self.win.flip()
            if key is None:
                return ('timeout', answer, resp_time-start_time)
            elif key == 'escape':
                print('quiting experiment')
                raise Exception('quiting')
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
            return ('timeout', answer, resp_time-start_time)
        elif key == 'escape':
            print('quiting experiment')
            raise Exception('quiting')
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
                win.close()
                core.quit() #change to close() for saving files
        self.win.flip()

    def text(self,  text,max_wait=3.0):
        display_text = visual.TextStim(self.win, text=text,
                                       font='Helvetica', alignHoriz='center',
                                       alignVert='center', units='norm',
                                       pos=(0,-0.8), height=0.08,
                                       color=[255, 255, 255], colorSpace='rgb255',
                                       wrapWidth=3)
        display_text.draw()
        self.win.flip()
        key = event.waitKeys(maxWait=max_wait)
        if key is not None:
            if key[0] == 'escape':
                print('quiting experiment')
                win.close()
                core.quit()
        self.win.flip()



def get_window():
    return visual.Window([900,900],
        winType='pyglet', monitor="testMonitor",fullscr=False, colorSpace='rgb',color=(-1,-1,-1),units='norm')

def autoDraw_on(stim):
    stim.autoDraw = True
    return stim

def autoDraw_off(stim):
    stim.autoDraw = False
    return stim

def run_vs(win, fi=None,setSize=4):
#    (expname, sid, numblocks, speed, mark_mode, input_mode) = get_settings()
    win.flip()
    timing = {'fixation': 0.8,
              'search': float('inf'),
              'blank': 2,
              'recall': 4 ,
              'intertrial': 1.0}
#
    orientation = [5,10,15] #replaced by staircase in the future
    orientation2 = [x*-1 for x in orientation]
    orientation=orientation+ orientation2

    #c [sqrt(0.005),0.2]; d1 [0.1,sqrt(4c**2-0.01)]
    constant = list(np.arange(0.08,0.2,0.02))
    d1=[]
    for i in range(len(constant)):
        a=list(np.arange(0.1,sqrt(4*constant[i]**2-0.01),0.02))
        d1.append([x for x in a if x<0.2])
    
    stim = Stimuli(win, timing, orientation)

    stim.text_and_stim_keypress('Welcome to the attention and working memory study',pos=(0,0.7),
                                stim=stim.ready)
    stim.text_and_stim_keypress('This is a visual search task',pos=(0,0.7),
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
    shuffle(trial_list)
    print (len(trial_list))
    # run trials
    for i, trial in enumerate(trial_list):
        try:
            resp, answer, rt, NN = stim.search_array(trial,condition='vs',setSize=setSize)
            corr = (resp == answer)
            if not corr:
                if resp == 'timeout':
                    stim.text('Timeout',max_wait=0.6)
                else:
                    stim.text('Incorrect',max_wait=0.6)
                   # condition', 'answer', 'response', 'RT', 'N/T similarity','N/N similarity','orientation'
            if fi is not None:
                fi.writerow(['%s, %s, %s, %.3f, %.2f, %.2f, %d\n'%('vs', answer, resp, rt, trial['c'], NN, 0)])
            core.wait(timing['intertrial'])
        except Exception as err:
            if err =='quiting':
                raise Exception('quiting')
            else:
                traceback.print_exc()
                raise Exception('quiting')
            
            
    stim.text_and_stim_keypress('Congratulations! You have finished.',
                                        max_wait=2.0)


def run_memory(win,fi, setSize=3):
#    (expname, sid, numblocks, speed, mark_mode, input_mode) = get_settings()
    

    win.flip()
    timing = {'fixation': 0.8,
              'search': 5,
              'blank': 2,
              'recall': 4 ,
              'intertrial': 1.0}
#
    orientation = [5,10,15] #staircase
    orientation2 = [x*-1 for x in orientation]
    orientation=orientation+ orientation2
    constant = list(np.arange(0.08,0.2,0.02))
    d1=[]
    for i in range(len(constant)):
        a=list(np.arange(0.1,sqrt(4*constant[i]**2-0.01),0.02))
        d1.append([x for x in a if x<0.2])

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
                fi.writerow(['%s, %s, %s, %.3f, %.2f, %.2f, %d\n'%('memory', answer, resp, rt, trial['c'], NN, trial['ori'])])
            core.wait(timing['intertrial'])
        except Exception as err:
            if err =='quiting':
                raise Exception('quiting')
            else:
                traceback.print_exc()
                raise Exception('quiting')
            
            
        
#        with open(expname + '_' + sid + '.json', 'a') as f:
#            f.write(json.dumps(block))
#            f.write('\n')
        
    stim.text_and_stim_keypress('Congratulations! You have finished.',
                                        max_wait=2.0)


def get_settings():
    data={}
    data['expname']='Attention_WM'
    data['expdate']=datetime.now().strftime('%Y%m%d_%H%M')
    data['PID']=''
    data['condition']=['vs','memory']
    dlg=gui.DlgFromDict(data,title='Exp Info',fixed=['expname','expdate'],order=['expname','expdate','PID','condition'])

    if not dlg.OK:
        core.quit()
    outName='P%s_%s.csv'%(data['PID'],data['expdate'])
    outFile = open(outName, 'wb')
    outWr = csv.writer(outFile, delimiter=';',quotechar=' ', quoting=csv.QUOTE_MINIMAL) # a .csv file with that name. Could be improved, but gives us some control
    outWr.writerow(['%s, %s, %s, %s, %s,%s, %s'%('condition', 'answer', 'response', 'RT', 'N/T similarity','N/N similarity','orientation')]) # write out header
    return outWr, outFile, data['condition']


    #cleanup/file closing/participant thank you messag
def close(win, fname=None):
    if fname is not None:
        fname.close() #close the output file
    thanks = visual.TextStim(win,'thank you for your participation',font='Helvetica', alignHoriz='center',
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
            run_memory(win,filewriter,setSize=4)
        except Exception:        
            close(win,fname=fname)
    else:
        try:
            run_vs(win,filewriter)
        except Exception:        
            close(win,fname=fname)