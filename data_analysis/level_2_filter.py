from patterns import Patterns
from event_factory import Event
from datetime import datetime

def do_events_match(pattern: Patterns, level_1_event: Event)-> bool:
    result = False
    number_of_appliances = len(pattern.appliances)
    print
    for i in range(number_of_appliances):
        if (datetime.strptime(pattern.appliance_start_times[i],'%H:%M:%S').time() == level_1_event.occured.time() and pattern.appliances[i] == level_1_event.appliance):
            result = True
            print("Got a match!")
            break
    return result


def filter_level_2_events(level_1_events: list, level_2_events: list())-> None:
    for pattern in level_2_events:        
        for lvl_1_event in level_1_events: 
            if(do_events_match(pattern, lvl_1_event)):
                level_1_events.remove(lvl_1_event)
    return

