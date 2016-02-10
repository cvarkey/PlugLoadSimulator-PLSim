from graph_data import make_graph, show_graph
from randtest_input_generator import generate_test_input
from inputstr_generator import InputGenerator
from goody import input_int, input_str

import device_parser
import device_sim

def convert_time(time: int, int_period: int):
    '''converts time in minutes to the time in int_periods which is measured in seconds
    ie  5 minutes = 60 int_periods when int_period = 5s'''
    
    return 60/int_period * time

def input_at_interval(ig_list: [InputGenerator], time_interval: int):
    for inp_gen in ig_list:
        inp = input_str('Are you using the {} [yes/no]: '.format(inp_gen.dev_name), {'yes', 'y', 'no', 'n'})
        if inp.lower() in ['yes', 'y']:
            state = input_str('Which of the following states is it in {}: '.format(inp_gen.states()), valid=inp_gen.states())
            inp_gen.write_on_state(state, time_interval)
        elif inp.lower() in ['no', 'n']:
            inp_gen.write_on_state('off', time_interval)


def main():
    device_map = device_parser.build_device_map(device_parser.parse_device('test.xml'))
    
    time = input_int('How long is this testing period (in minutes): ')
    integration_period = input_int("integration factor (in seconds): ")
    
    num_int_periods = int(convert_time(time, integration_period))+1
   
    input_generators = []
    
    for k,v in device_map.items():
        input_generators.append(InputGenerator(k, set(v.keys()), num_int_periods))
        
    print('\nInput the start states:')    
    input_at_interval(input_generators, 1)
    while not input_generators[0].is_full():
        print()
        time_interval = input_int('How long is this time interval (in minutes): ')
        num_periods_interval = int(convert_time(time_interval, integration_period))
        input_at_interval(input_generators, num_periods_interval)
        
    with open('test_input_manual.csv', 'w') as outfile:
        to_write = ''
        for input_generator in input_generators:
            to_write += input_generator.generate_str()
        outfile.write(to_write)
        
    power_map = device_sim.parse_inputfile('test_input_manual.csv', device_map)
    power_matrix = list(power_map.values())       
    power_array = device_sim.flatten_cols(power_matrix)
    print('\nEnergy Used: ', device_sim.energy_used(power_array, integration_period), 'Watt-hours')
    make_graph(power_array, integration_period)
    show_graph()

    
def test():
    device_map = device_parser.build_device_map(device_parser.parse_device('test.xml'))
    generate_test_input(device_map, 2880, file_name='test_input1.csv')
    
    
    power_map = device_sim.parse_inputfile('test_input.csv', device_map)
     
    power_matrix = list(power_map.values())
    
    integration_period = int(input("integration factor (in seconds): "))
          
    power_array = device_sim.flatten_cols(power_matrix)
    print(device_sim.energy_used(power_array, integration_period), 'Watt-hours')

    make_graph(power_array, integration_period)
    show_graph()

if __name__ == '__main__':
    main()
    #test()
    pass
