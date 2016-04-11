'''
Created on Apr 11, 2016

@author: Klint
'''


class AdvancedPowerStrip:
    
    ''' This class models an advanced power strip, power strip that automatically disconnects certain devices when
    certain conditions are met. Ie. No Infrared is Sensed and/or No Movement
    
    (put a plaintxt diagram here)
    '''
    
    def __init__(self, independent_devices: str, dependendent_devices: list, time_limit: int, is_on = False):
        self._independent_device     = independent_devices
        self._independent_device_on  =  is_on;
        self._dependendent_devices   = dependendent_devices
        self._time_limit             = time_limit
        
    def turn_on_independent_device(self):
        self._independent_device_on  = True
        
    def turn_off_independent_device(self):
        self._independent_device_off = False
    