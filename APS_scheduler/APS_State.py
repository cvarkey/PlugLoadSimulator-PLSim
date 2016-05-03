'''
this module contains APS_State classes, this class controls the APS wrt. to time
'''

from APS_scheduler.Advanced_Power_Strip import AdvancedPowerStripT2 as APS_T2
from PlugLoad_Sim.inputstr_generator import InputGenerator

from collections import deque

import sys

# TODO
# handling case where a state is carried over elegantly

INF = float('inf')

class APSStateError:
    pass

class APS2_State:
    '''
    models trickle star APS Plus which follows this logic
    
    This power strip automatically disconnects certain devices when
    certain conditions are met. Ie. No Infrared is Sensed and/or No Movement
    
    Diagram of the APS logic 
    
    IR -> switch devices on(standby) -> user turns TV on <----------------
                                            |                            ^
                                           \/                            |
                           [time_limit] minutes of IR only detection -> YES <---
                                            |                                   |
                                           \/                                   | 
                                           NO --> [move_time] IR OR Movement-->YES
                                            |
                                           \/
                                          TV off --> slave devices off                 
    '''
    
    
    # Interface:
    # constructor: takes in APS class instance of the times that APS use, str_generators for generating strings
    # flush      : reset internal deque, then write to the generators, used at the end  of an input interval
    # get_state  : gets the current state should be used to determine the prompt
    # 
    
    
    # Notes on Implementation
    # all math must be done in terms of number of periods
    # use deque to add on state:time pairs to write to str_generators
    
    # modes that APS State can be in
    IR          = 'IR_only'
    IR_AND_MOVE = 'IR_and_movement'
    POWER_SAVE  = 'power_save'
    
    NEXT_STATES_SIGNAL   = {IR: IR, IR_AND_MOVE: IR, POWER_SAVE:POWER_SAVE}
    NEXT_STATES_NOSIGNAL = {IR: IR_AND_MOVE, IR_AND_MOVE: POWER_SAVE, POWER_SAVE:POWER_SAVE}
    
    def __init__(self, aps: APS_T2, interval_periods: int, start_state=IR, start_periods=0):
        self._aps          = aps
        self._time_map     = {APS2_State.IR: aps.time_IR_only(), 
                              APS2_State.IR_AND_MOVE: aps.time_IR_and_movement(), 
                              APS2_State.POWER_SAVE: INF}
        
        self._current_time = 0
        self._max_periods  = interval_periods
        self._time_left    = self._max_period
    
        self._state        = start_state
        self._states_times = deque(start_state, start_periods)
    
        self._carry_over   = None # carry_over corner case this will 
        
    def time_left(self):
        return self._time_left
        
    def flush(self):
        '''
        call at the end of the interval flushes the deque which contains the information about the states
        and the times spent at each state
        '''
        
        
        # perform checks for the deques time adding up to the interval time
        sum = 0
        for state, time in self._states_times:
            sum += time
        if sum > self._max_periods:
            raise APSStateError('Error in aligning deque: Time alloted is greater than time in interval')
        
        
        return self._states_times

    def check_state(self):
        return self._state
    
    def input_signal(self, time: int):
        '''
        input a signal with time after the last signal in intervals,
        this time cannot be more than the threshold until the APS changes to its next state
        if this method is called the current state is written with the amount of time until the signal
        '''
        if self._state == APS2_State.POWER_SAVE:
            raise APSStateError('State cannot be {} in method: input signal'.format(APS2_State.POWER_SAVE))
        if time > self._time_map[self._state]:
            raise APSStateError('Method: input_signal: \
            Time inputed {} is greater than maximum allowed time {} in current state: {}'.format(
            time, self._time_map[self._state], self._state))
            
        self._current_time += time
        self._time_left     = self._max_periods - self._current_time # make sure that this is correct
        
        old_state = self._state
        self._state = APS2_State.NEXT_STATES_SIGNAL[old_state]
        
        self._states_times.append(old_state, min(time, self._time_left))
        
    def next_state(self):
        '''
        call if there is no signal inputed within the threshold that the state provides, moves the device
        to the next state while also doing all the time consideration
        '''
        old_state   = self._state
        
        self._states_times.append(old_state, min(self._time_map[old_state], self._time_left))
        
        self._current_time += min(self._time_map[old_state], self._time_left)
        self._time_left     = self._max_periods - self._current_time
        
        
        
        
        
        
        
        
        
    
    
    