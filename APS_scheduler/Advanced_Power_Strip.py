'''
Created on Apr 11, 2016

@author: Klint
'''


class AdvancedPowerStrip:
    
    ''' This class models an advanced power strip, power strip that automatically disconnects certain devices when
    certain conditions are met. Ie. No Infrared is Sensed and/or No Movement
    
    (put a plaintxt diagram here)
    '''
    
    def __init__(self, master_devices: str, slave_devices: list, time_limit: int, is_on = False):
        self._master_device     = master_devices
        self._slave_devices     = slave_devices
        self._time_limit        = time_limit
        self._music_mode        = False
        
        self._master_device_on  = is_on
        self._slave_devices_on  = is_on
        
    def turn_on_master_device(self):
        self._master_device_on  = True
        self._slave_devices_on  = True
        
    def turn_off_master_device(self):
        self._master_device_on  = False
        
        if(not self._music_mode):
            self._slave_devices_on = True
            
    def turn_on_music_mode(self):
        self._music_mode = True
        
    def turn_off_music_mode(self):
        self._music_mode = False
    