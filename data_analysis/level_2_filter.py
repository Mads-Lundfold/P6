from patterns import Patterns
from event_factory import Event
from datetime import datetime
from typing import List

def do_events_match(pattern: Patterns, level_1_event: Event)-> bool:
    result = False
    number_of_appliances = len(pattern.appliances)
    for i in range(number_of_appliances):
        if (datetime.strptime(pattern.appliance_start_times[i],'%H:%M:%S').time() == level_1_event.occured.time() and pattern.appliances[i] == level_1_event.appliance):
            result = True
            print("Matching level 1 event found in lvl 2 pattern!")
            break
    return result


def filter_level_2_events(level_1_events: list, level_2_events: list)-> list:
    lvl_2_patterns = list()
    for pattern in level_2_events:
        lvl_2_dict = dict()
        lvl_2_dict['relation'] = pattern.relation
        lvl_2_dict['events'] = list()   
        for lvl_1_event in level_1_events: 
            if(do_events_match(pattern, lvl_1_event)):
                lvl_2_dict['events'].append(lvl_1_event)
                #level_1_events.remove(lvl_1_event)
        if len(lvl_2_dict['events']) == 2:
            lvl_2_patterns.append(lvl_2_dict)
    return lvl_2_patterns

