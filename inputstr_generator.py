'''
Input Generator class

@author: Klint
'''

class InputGenerator:
    
    def __init__(self, device: str, states: set, m_size: int):
        
        self.dev_name = device
        self._dev_strdict = self._make_strdict(states)
        self._max_size = m_size
        self._curr_time = 0
    
    def _make_strdict(self, states: set):
        to_return = {};
        for state in states:
            to_return[state] = ''
        return to_return
    
    def write_on_state(self, state: str, int_time: int):
        time_left = self._max_size - self._curr_time
        if int_time > time_left: # may throw error here idk yet
            int_time = time_left
        
        for key in self._dev_strdict.keys():
            if key == state:
                self._dev_strdict[key] += int_time*'1'
            else:
                self._dev_strdict[key] += int_time*'0'
        
        self._curr_time += int_time
        
    def states(self):
        return set(self._dev_strdict.keys())
    
    def is_full(self):
        return self._max_size == self._curr_time
    
    def _build_str(self):
        template = '{},{},{}\n'
        to_return = ''
        
        for k,v in self._dev_strdict.items():
            to_return += template.format(self.dev_name, k, v)
        
        return to_return
    
    def generate_str(self):
        if not self.is_full():
            print('error') # do errors later
            return
            
        return self._build_str()
    
    def __repr__(self):
        to_return  = 'max_size: {}, is_full: {}\n'.format(self._max_size, self.is_full())
        to_return += self._build_str()
        return to_return

if __name__ == '__main__':
    i1 = InputGenerator('tv', {'on', 'off', 'standby'}, 100)
    
    i1.write_on_state('on', 25)
    print(i1)
    i1.write_on_state('off', 50)
    i1.write_on_state('standby', 25)
    
    assert i1.is_full()
    i_str = i1.generate_str()
    print(i_str)
    
    