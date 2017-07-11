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
import itertools, csv, sys, os.path
from random import shuffle
import numpy as np
from copy import copy


class Stimuli:

    def __init__(self, win, timing, orientation):
        self.win = win
        self.timing = timing
        self.orientation=orientation
        
        self.fixation = visual.TextStim(self.win, text='+',
                                        alignHoriz='center',
                                        alignVert='center', units='norm',
                                        pos=(0, 0), height=0.3,
                                        color=[255, 255, 255], colorSpace='rgb255',
                                        wrapWidth=2)
        self.probe = visual.TextStim(self.win,text='clokwise or anticlockwise?',
                                     font='Helvetica', alignHoriz='center', alignVert='center',
                                     units='norm',pos=(0, 0.5), height=0.1,
                                     color=[255, 255, 255], colorSpace='rgb255',wrapWidth=2)
        self.recall_keymap = {'z': 'clockwise', 'm': 'anticlockwise'}
        
#        c  mean N/T similarity 0< c <0.2
#        d1# D1/T similarity 0< d1 <c
    def make_stim (self, c, d1, Type,size=0.15, lw=2):  
        d2 = [2*c-d1,d1-2*c]
        vertice = []
        vertice.append([(0, 0), (.2, 0), (.2, .4),(.2, 0),(.4,0)])
        vertice.append([(0, 0), (.2-d1, 0), (.2-d1, .4),(.2-d1, 0),(.4,0)])
        vertice.append([(0, 0), (.2-d2[0], 0), (.2-d2[0], .4),(.2-d2[0], 0),(.4,0)])
        vertice.append([(0, 0), (.2-d2[1], 0), (.2-d2[1], .4),(.2-d2[1], 0),(.4,0)])
        if Type=='t':
            return visual.ShapeStim(self.win, vertices=vertice[0],
                                 closeShape=False, lineWidth=lw, 
                                 ori=0,size=size,name='target',autoDraw=False)
        if Type=='d1':
            return visual.ShapeStim(self.win, vertices=vertice[1],
                                 closeShape=False, lineWidth=lw, 
                                 ori=0,size=size,name='d1',autoDraw=False)
        if Type=='d2_1':
            return visual.ShapeStim(self.win, vertices=vertice[2],
                                 closeShape=False, lineWidth=lw, 
                                 ori=0,size=size,name='d2_1',autoDraw=False)
        if Type=='d2_2':
            return visual.ShapeStim(self.win, vertices=vertice[3],
                                 closeShape=False, lineWidth=lw, 
                                 ori=0,size=size,name='d2_2',autoDraw=False)
 

    def get_input(self, max_wait=3.0, keylist=None):
        key = event.waitKeys(maxWait=max_wait, keyList=keylist,timeStamped=True)
        if key is not None:
            key = key[0]
        time = key[0][1]

        return (key, time)


    def draw_fixation(self):
        self.fixation.draw()
        self.win.flip()
        core.wait(self.timing['fixation'])
        self.win.flip()

    #adjust distractor difficulty and draw search array 
    def search_array(self, trial):#trial contains [c, d1, ori, hard or easy(d1 or d2)]
        self.draw_fixation()
        draw_objs = []
        
        stimpos = list(itertools.product(np.linspace(-0.3,-0.3,num=6),np.linspace(-0.3,0.3,num=6))) #set1
        stimori = list(np.random.randint(2,size=6**2))
        map(lambda x:x*10,stimori)
        for n in range((len(stimpos)-1)/2):
            draw_objs.append(make_stim(c=trial['c'], d1=trial['d1'], Type='d1'))
            draw_objs.append(make_stim(c=trial['c'], d1=trial['d1'], Type=trial['level']))
            
        draw_objs.append(make_stim(c=trial['c'], d1=trial['d1'], Type='T'))
        draw_objs.append(make_stim(c=trial['c'], d1=trial['d1'], Type='d1'))
        shuffle( draw_objs)
        [x.setPos(y) for x,y in zip(draw_objs,stimpos)]
        [x.setOri(y) for x,y in zip(draw_objs,stimori)]
        
        map(autoDraw_on, draw_objs)
        self.win.flip()
        key, resp_time = self.get_input(max_wait=self.timing['search'],
                                        keylist=['escape'])
        if key is None:
            pass
        else:
            print('quiting experiment')
            core.quit() #change to close() for saving files
        map(autoDraw_off, draw_objs)
        self.win.flip()
        #delay blank screen
        key, resp_time = self.get_input(max_wait=self.timing['blank'],
                                        keylist=['escape'])
        if key is None:
            pass
        else:
            print('quiting experiment')
            core.quit() #change to close() for saving files
            
        #draw the rotated target and ask for a binary response
    def recall(self):
        target_probe = copy(self.target)
        target_probe.ori = self.orientation
        if self.orientation >=0:
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
            core.quit() #change to close() for saving files
        else:
            return (self.recall_keymap[key], answer, resp_time-start_time)#return response, correct answer &RT

    def text_and_stim_keypress(self, text, stim=None, max_wait=float('inf')):
        if stim is not None:
            if type(stim) == list:
                map(lambda x: x.draw(), stim)
            else:
                stim.draw()
        display_text = visual.TextStim(self.win, text=text,
                                       font='Helvetica', alignHoriz='center',
                                       alignVert='center', units='norm',
                                       pos=(0, -0.8), height=0.1,
                                       color=[255, 255, 255], colorSpace='rgb255',
                                       wrapWidth=2)
        display_text.draw()
        self.win.flip()
        key = event.waitKeys(maxWait=max_wait)
        if key is not None:
            if key[0] == 'escape':
                print('quiting experiment')
                core.quit() #change to close() for saving files
        self.win.flip()

    def text(self, text):
        display_text = visual.TextStim(self.win, text=text,
                                       font='Helvetica', alignHoriz='center',
                                       alignVert='center', units='norm',
                                       pos=(0, 0), height=0.1,
                                       color=[255, 255, 255], colorSpace='rgb255',
                                       wrapWidth=2)
        display_text.draw()
        self.win.flip()
        key = event.waitKeys(maxWait=max_wait)
        if key is not None:
            if key[0] == 'escape':
                print('quiting experiment')
                core.quit() #change to close() for saving files
        self.win.flip()

def get_settings():
    data={}
    data['expname']='Attention_WM'
    data['expdate']=datetime.now().strftime('%Y%m%d_%H%M')
    data['PID']=''
    dlg=gui.DlgFromDict(data,title='Exp Info',fixed=['expname','expdate'],order=['expname','expdate','PID'])
    if not dlg.OK:
        core.quit()
#    outName='P%s_%s.csv'%(data['participantid'],data['expdate'])
#    outFile = open(outName, 'wb')
#    outWr = csv.writer(outFile) # a .csv file with that name. Could be improved, but gives us some control
#    outWr.writerow(['%s, %s, %s, %s, %s\n'%('condition', 'trial_no', 'target', 'response', 'Reaction time')]) # write out header
#    return outFile

def get_window():
    return visual.Window([1024,768],
        winType='pyglet', monitor="testMonitor",fullscr=False, colorSpace='rgb255')

def autoDraw_on(stim):
    stim.autoDraw = True
    return stim

def autoDraw_off(stim):
    stim.autoDraw = False
    return stim

def run():
    (expname, sid, numblocks, speed, mark_mode, input_mode) = get_settings()
    win = get_window()

    win.flip()
    timing = {'fixation': 0.5,
              'search': 2.0,
              'blank': 2,
              'recall': 3 / speed,
              'intertrial': 0.5 / speed}
    colors = {'red': (227, 2, 24),
              'green': (95, 180, 46),
              'blue': (48, 62, 152),
              'yellow': (251, 189, 18)}
    orientation = {} #staircase
    constant = {}
    d1={} 
    stim = Stimuli(win, timing, colors, mark_mode, input_mode)

    stim.text_and_stim_keypress('First you will see a circle. Remember its color.',
                                stim=stim.cue)
    stim.text_and_stim_keypress('Afterward, find the tilted line.\nPress 1 if the line is tilted left. Press 2 if the line is tilted right.',
                                [stim.search['top'], stim.search['bot'],
                                 stim.line[('top', 'left')], stim.line[('bot', 'straight')]])
    stim.text_and_stim_keypress('At the end, we will ask you the color of the first circle you saw.', stim=stim.memory[1:])
    stim.text_and_stim_keypress('Press any key when ready to begin!')
    # the first color is the search target, second is the distractor
    trial_types = [('red', 'blue'), ('red', 'green'), ('red', 'yellow'),
                   ('blue', 'red'), ('blue', 'green'), ('blue', 'yellow'),
                   ('green', 'red'), ('green', 'blue'), ('green', 'yellow'),
                   ('yellow', 'red'), ('yellow', 'green'), ('yellow', 'blue')]
    block_list = []

    # construct blocks
    for block_num in range(numblocks):
        block = {}
        block['speed_factor'] = speed
        block['block_num'] = block_num
        block['cue_color'] = random.choice(colors.keys())
        random.shuffle(trial_types)
        trial_list = []
        # construct trials
        for trial_num in range(len(trial_types)):
            trial = {}
            trial['trial_num'] = trial_num
            trial['target_type'] = random.choice(['left', 'right'])
            trial['search_colors'] = trial_types[trial_num]
            target_col = trial['search_colors'][0]
            distract_col = trial['search_colors'][1]
            if block['cue_color'] == target_col:
                trial['validity'] = 'valid'
            elif block['cue_color'] == distract_col:
                trial['validity'] = 'invalid'
            else:
                trial['validity'] = 'neutral'
            trial['target_pos'] = random.choice(['top', 'bot'])
            trial_list.append(trial)
        block['trials'] = trial_list
        block_list.append(block)

    # sequence to mark beginning of trial
    stim.mark_task('begin')
    core.wait(1.0)

    # run trials
    for block_num in range(len(block_list)):
        block = block_list[block_num]
        block['fixation_on'] = core.getTime()
        stim.draw_fixation()
        block['fixation_off'] = core.getTime()
        block['cue_on'] = core.getTime()
        block['cue_off'] = stim.draw_cue(block['cue_color'])
        for trial_num in range(len(block['trials'])):
            trial = block['trials'][trial_num]
            resp, start_time, off_time, end_time = stim.do_search(trial)
            block['trials'][trial_num]['search_response'] = resp
            block['trials'][trial_num]['search_start_time'] = start_time
            block['trials'][trial_num]['search_off_time'] = off_time
            block['trials'][trial_num]['search_resp_time'] = end_time
            corr = (resp == trial['target_type'])
            block['trials'][trial_num]['search_correct'] = corr
            if not corr:
                if resp == 'timeout':
                    stim.text('Timeout')
                else:
                    stim.text('Incorrect')
            core.wait(timing['intertrial'])
        chosen_col, start_time, end_time = stim.do_memory()
        block_list[block_num]['mem_response'] = chosen_col
        block_list[block_num]['mem_response_start'] = start_time
        block_list[block_num]['mem_response_resp'] = end_time
        corr = (chosen_col == block['cue_color'])
        block_list[block_num]['mem_correct'] = corr
        if corr:
            stim.text('Correct!')
        elif chosen_col == 'timeout':
            stim.text('Timeout')
        else:
            stim.text('Incorrect')
        core.wait(timing['intertrial'])
        with open(expname + '_' + sid + '.json', 'a') as f:
            f.write(json.dumps(block))
            f.write('\n')
        if block_num < len(block_list) - 1:
            stim.text_and_stim_keypress('Press escape to quit.', max_wait=2.0)
        else:
            stim.text_and_stim_keypress('Congratulations! You have finished.',
                                        max_wait=2.0)
    return win

    '''
    cleanup/file closing/participant thank you message
    '''
def close(fname,win):

    fname.close() #close the output file
    thanks = visual.TextStim(win,'thank you for your participation',font='Helvetica', alignHoriz='center',
                          alignVert='center', units='norm', height=0.1,color=(1.0,1.0,1.0))    
    thanks.draw()
    win.flip()
    event.waitKeys(keyList=['return'])    
    win.close()     #close the psychopy windo
    core.quit()
    print "all tests concluded"    



if __name__ == '__main__':
    win = run()
    fname = get_settings()
    close(fname,win)