''' This module parses through XML file and creates a an instance of a Device
    class Device has 2 fields. a name and a map representing states and how much
    power they use. XML files follows this template:
    
        <device = name>
            [<state: name, power>
            <\state>]
        \<device>
'''

import xml.etree.ElementTree as ET
        
def parse_device(xml: str)->ET:
    tree = ET.parse(xml)
    root = tree.getroot()
    return root

def build_device(tree: ET):
    device_name = tree.get('name')
    
    device_states = {}
    for child in tree:
        device_states[child.get('name')] = int(child.text)
    
    return (device_name, device_states)

def build_device_map(tree: ET)->dict:
    to_return = {}
    
    for child in tree:
        device = build_device(child)
        to_return[device[0]] = device[1]
    
    return to_return


if __name__ == '__main__':
    print(build_device_map(parse_device('test.xml')))

        


            