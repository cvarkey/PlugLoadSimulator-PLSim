'''
Created on Apr 15, 2016

@author: Klint
'''
from PlugLoad_Sim.inputstr_generator import make_input_generators, NameGenerator
from PlugLoad_Sim.goody import input_int, input_str, input_str_with_nummap
from PlugLoad_Sim.device_sim import write_to_ifile, analyze_data
from APS_scheduler.Advanced_Power_Strip import AdvancedPowerStripT2
from PlugLoad_Sim.inputstr_generator import InputGenerator

import PlugLoad_Sim.device_parser as device_parser
 
 
# bug list
# 1. adds 60 minutes to the APS thing no matter yet
#       a. quick disgusting fix: just subtract 60 from whatever

OFF_STATE     = 'off'     # denotes which state consumes 0 power each state must be the same in all devices
DEFAULT_STATE = 'standby' # these 2 states must ALWAYS be denoted in the XML file for this program to work

YES_NO_INPUTS = {'yes', 'y', 'no', 'n'}

MENU_STR = '''MENU:
a: add a device
d: delete a device
p: print the devices you have
r: run the simulation
q: quit
'''

def convert_time(time: int, int_period: int):
    '''converts time in minutes to the time in int_periods which is measured in seconds
    ie  5 minutes = 60 int_periods when int_period = 5s'''
    
    return 60/int_period * time

def input_device_model(devices_data: {dict}, p_string: str)->list:
    if type(devices_data) == set:
        z = zip(range(1, len(devices_data)+1), devices_data)
        inp = input_str_with_nummap('Which type of {} device do you want to choose? {}'.format(p_string, 
                    sorted(z)), devices_data)
        print('selected: {}'.format(inp))
        return [inp]
    else:
        keys_set = set(devices_data.keys())
        z = zip(range(1, len(keys_set)+1), keys_set)
        
        inp = input_str_with_nummap('Which type of {} device do you want to choose? {}'.format(
                                    p_string, sorted(z)), keys_set)
        
        p_string += '{}:'.format(inp)
        to_return = [inp]
        print('selected: {}'.format(inp))
        to_return.extend(input_device_model(devices_data[inp], p_string))
            
        return to_return

def create_ig_map(ig_list: list):
    return {d.dev_name: d for d in ig_list}

def get_unbound_devices(ig_map: dict, aps):
    return set(filter(lambda x: not x in aps.slave_devices() and x != aps.master_device() and x != 'aps',
                             ig_map.keys()))

def get_states(ig_map, devices: {str}, time_interval: int):
    '''
    takes in a list of devices and asks user whether or not that device is being used
    then writes onto the string generators the specified time interval
    '''
    result = {}
    
    for d in devices:
        inp = input_str('Are you using the {} [yes/no]: '.format(d), {'yes', 'y', 'no', 'n'})
        if inp.lower() in ['yes', 'y']:
            rlen = range(1, len(ig_map[d].states())+1)
            str_rlen = set(str(x) for x in rlen)
            state = input_str('Which of the following states is it in {}: '.format(
                              sorted(zip(rlen, ig_map[d].states()))), valid=ig_map[d].states().union(str_rlen))
            
            input_dict = dict(zip(rlen, ig_map[d].states()))
            if not state in ig_map[d].states():
                state = input_dict[int(state)]
                
            ig_map[d].write_on_state(state, time_interval)
            result[d] = state
        elif inp.lower() in ['no', 'n']:
            ig_map[d].write_on_state(DEFAULT_STATE, time_interval)
            result[d] = DEFAULT_STATE
            
    return result

def write_aps_states(master_device, master_state, slave_states, ig_map, n_periods):
    ig_map[master_device].write_on_state(master_state, n_periods)
    for k,v in slave_states.items():
        ig_map[k].write_on_state(v, n_periods)

def input_at_interval(ig_map: ['InputGenerator'], time_info: tuple, unbound_devices: {str}, aps: AdvancedPowerStripT2):
    '''helper function for running the simulation, at each time interval it asks whether or not the
    device is being used then uses the writes'''
    
    ### this function is a mess refactor it into several functions at some point
    
    n_periods, n_periods_IR, n_periods_move_IR, int_period = time_info
    current_period = min(n_periods_IR, n_periods)
    
    master_device = aps.master_device()
    slave_devices = aps.slave_devices()
    
    # get states for the devices that are independent of the APS
    get_states(ig_map, unbound_devices, n_periods)
    
    print('Enter the states for the master device: ')
    master_info  = get_states(ig_map, {master_device}, current_period) # this causes the added sixty minutes bug
    master_state = master_info[master_device]
    slave_states = {}
    
    # CASE I: master is off APS turns off slave devices
    if master_state == DEFAULT_STATE or master_state == OFF_STATE:
        aps.turn_off_master_device()
        ig_map[master_device].write_on_state(master_state, n_periods-current_period)
        for d in slave_devices:
            ig_map[d].write_on_state(OFF_STATE, n_periods)
        return
    else:
        aps.turn_on_master_device()
        if aps.slave_devices_on():
            slave_states = get_states(ig_map, slave_devices, current_period)
        
    
    # CASE II: master is ON triggers APS T2
    n_periods_lastIR = 0
    n_periods_lastMoveIR = 0
    
    slave_off = dict((k, OFF_STATE) for k in slave_devices)
    
    #
    # everything from below this point will likely be refactored.
    #
    
    while current_period < n_periods:
        periods_left = n_periods - current_period
        
        if periods_left > n_periods_IR:
            inp = input_str('In the last {} has there been any IR signal? '.format(aps.time_IR_only()), valid=YES_NO_INPUTS)
            
            if inp.lower() in {'y', 'Yes'}:
                last_IR = input_int('How long ago was the last IR signal detected? ', 
                                    valid=set(range(0, aps.time_IR_only())))
                n_periods_lastIR = n_periods_IR - int(convert_time(last_IR, int_period))
                write_aps_states(master_device, master_state, slave_states, ig_map, n_periods_lastIR)
                
                current_period += n_periods_lastIR
                periods_left = n_periods - current_period
                
            else:
                if periods_left > n_periods_move_IR:
                    inp = input_str('In the last {} has there been any IR signal or movement? '.format(aps.time_IR_and_movement()),
                                     valid=YES_NO_INPUTS)
                    
                    if inp.lower() in {'y', 'Yes'}:
                        last_IR_move = input_int('How long ago was the last IR signal or movement detected? ', 
                                            valid=set(range(0, aps.time_IR_and_movement())))
                        n_periods_lastMoveIR = n_periods_move_IR - int(convert_time(last_IR_move, int_period))
                        write_aps_states(master_device, master_state, slave_states, ig_map, n_periods_lastMoveIR)
                        
                        current_period += n_periods_lastMoveIR
                        periods_left = n_periods - current_period
                    
                    else:
                        n_periods_to_add = int(convert_time(aps.time_IR_only(), int_period)) +\
                                           int(convert_time(aps.time_IR_and_movement(), int_period))
                                                          
                        write_aps_states(master_device, master_state, slave_states, ig_map, n_periods_to_add)
                        current_period += n_periods_to_add
                        periods_left = n_periods - current_period
                        
                        write_aps_states(master_device, master_state, slave_off, ig_map, periods_left)
                        break
                else:
                    write_aps_states(master_device, master_state, slave_states, ig_map, periods_left)
                    current_period += periods_left # cause a break
                    break
            
        else: # periods_left < n_periods_IR
            write_aps_states(master_device, master_state, slave_states, ig_map, periods_left)
                
            current_period += periods_left # cause a break
            break
            
            

def run_sim(integration_period: int, input_generators: dict, aps: AdvancedPowerStripT2):
    '''runs the simulation that creates the input csv'''
    print('\nInput the start states:')  
    unbound_devices = get_unbound_devices(input_generators, aps)
  
    input_at_interval(input_generators, (1,10,10,integration_period), unbound_devices, aps)
    
    while True:
        print()
        time_interval = input_int('How long is this time interval (in minutes)[enter 0 to end the simulation]: ')
        if time_interval == 0:
            break
        
        num_periods_interval = int(convert_time(time_interval, integration_period))
        num_periods_IR       = int(convert_time(aps.time_IR_only(), integration_period)) 
        num_periods_IRmove   = int(convert_time(aps.time_IR_and_movement(), integration_period)) 
        
        time_info = (num_periods_interval, num_periods_IR, num_periods_IRmove, integration_period)
        
        input_at_interval(input_generators, time_info, unbound_devices, aps)

def main():
    name_gen = NameGenerator()
    device_map = {}
    tree = device_parser.parse_data('../xmls/data_grouped.xml')
    devices_data = device_parser.parse_groupings(tree) # could become a bottleneck if xmls get large enough
    aps = None
    
    while True:
        inp = input_str(MENU_STR, valid={'a', 'p', 'r', 'q', 'd'})
        print()
        if inp == 'a':
            dev_key = input_device_model(devices_data, '')
            key,value = device_parser.search_data(tree, dev_key)
            device_map[name_gen.generate_name(key)] = value
        if inp == 'd':
            valid = set(device_map.keys())
            if len(valid) > 0:
                to_delete = input_str('Which device do you want to delete? {}: '.format(valid), valid)
                del device_map[to_delete]
            else:
                print('There are no devices to delete\n')
        if inp == 'p':
            print(set(device_map.keys()))
        if inp == 'c':
            pass
        if inp == 'r':
            input_generators = create_ig_map(make_input_generators(device_map))
            aps = AdvancedPowerStripT2('LG LED HiDef TV', ['Microsoft Xbox One', 'Dolby Surround Sound'], 60, move_time=75, is_on=False)

            integration_period = input_int('Enter integration period: ')
            run_sim(integration_period, input_generators, aps)
            
            device_map['aps'] = {'on': 1.5, 'off': 0.0}

            write_to_ifile('../csvs/test_APS.csv', integration_period, list(input_generators.values()))
            analyze_data('../csvs/test_APS.csv', integration_period, device_map)
        print()
        if inp == 'q':
            return
        
if __name__ == '__main__':
    main()
