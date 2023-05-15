import datetime
import sys
import time
import pandas as pd
import numpy as np
from data_analysis import get_data_from_house

from time_associations import get_quarter_tas
from electricity_price_dataset import read_extract_convert_price_dataset
from event_factory import EventFactory, Event
from level_2_filter import filter_level_2_events
from patterns import optimization_patterns, read_patterns_csv



class Optimizer:
    '''
    def __init__(self, events: Event, price_data, restricted_times, patterns):
        self.events = events
        self.price_data = price_data
        self.restricted_times = restricted_times
        self.patterns = patterns
    '''
    def __init__(self, time_assoications):
        self.time_assoications = time_assoications
    
    
    def optimize_day(self, events, price_vector, patterns):
        # List of the newly scheduled events
        #new_schedule = list()
        temp_available_times = self.time_assoications
        time_start = 0
        time_end = len(price_vector) - 1

        # call level2-filter to get list of lvl2 dicts}
        level2 = filter_level_2_events(events,patterns)
        print(level2)

        for pattern in level2:
            if pattern['relation'] == '>':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].timeslot, pattern['events'][0].endslot)
            if pattern['relation'] == '->':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end - pattern['events'][1].length)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].endslot, time_end)
            if pattern['relation'] == '|':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end - pattern['events'][1].length)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].endslot - pattern['events'][1].length, pattern['events'][0].endslot + pattern['events'][1].length)

        for event in events:
            self.place_event(event, price_vector, temp_available_times, time_start, time_end)
        

    def place_event(self, event: Event, price_vector: list, temp_available_times: dict, start_time: int, end_time: int):
        if event.placed:
            return 
        print(f'Timespan: {start_time} - {end_time}')

        event_len = event.length
        lowest_cost = sys.maxsize # Replace with its current price
        optimal_start = event.timeslot

        #print(event.appliance)
        #print(f'Available timeslots for {event.appliance}: \n {temp_available_times[event.appliance]}')

        for i in range(start_time, end_time - event_len):
            # Check if every timeslot of the event (starting in i) are available timeslots
            if all(timeslot in temp_available_times[event.appliance] for timeslot in [*range(i,i+event_len,1)]):
                # Calculate cost of placement
                new_cost = np.sum(event.profile * price_vector[i:i+event_len])
                
                # If cost is better than the previous best cost, update
                if new_cost < lowest_cost:
                    lowest_cost = new_cost
                    optimal_start = i

        # After the event has been placed, we remove its timeslots from the available times for the appliance.
        # If we have placed a laptop event at 12:00 - 12:30, we remove that time range from the available times for laptops,
        # so we can't place another laptop in that time range.
        taken_slots = range(optimal_start, optimal_start+event_len,1)
        temp_available_times[event.appliance] = list(set(temp_available_times[event.appliance]) - set(taken_slots))
        print(f'Timeslots where {event.appliance} has been placed: {taken_slots}')

        event.timeslot = optimal_start
        event.placed = True
        

    def find_total_cost_of_events(self, events: list, price_vector: list):
        total_cost = 0
        for event in events:
            cost = np.sum(event.profile * price_vector[event.timeslot : event.timeslot+event.length])
            total_cost = total_cost + cost
        return total_cost

    


def create_price_vector_dataset(start: int, end: int):
    price_data = read_extract_convert_price_dataset()
    price_data_2015 = price_data[price_data['unix_timestamp'].between(start, end)]

    price_data_2015['unix_timestamp'] = pd.to_datetime(price_data_2015['unix_timestamp'], unit='s').dt.strftime('%Y-%m-%d')

    price_data_2015 = price_data_2015.groupby('unix_timestamp')['GB_GBN_price_day_ahead'].apply(list)
    #print(price_data_2015)

    return price_data_2015


def main():
    house_3_tas = get_quarter_tas()
    #print(house_3_restricted_times)
    price_data_2015 = create_price_vector_dataset(1420066800, 1451602800)
    price_vector = np.array(np.repeat(price_data_2015['2015-03-27'],4))
    #price_vector = expand_price_vector(price_data_2015['2015-04-04'], 4)
    #print(price_vector)

    dataset = str(sys.argv[1])
    house_1 = dataset + "/house_1"
    house_2 = dataset + "/house_2"
    house_3 = dataset + "/house_3"
    house_4 = dataset + "/house_4"
    house_5 = dataset + "/house_5"

    watt_df, on_off_df = get_data_from_house(house_number = house_3) 

    event_fac = EventFactory(watt_df=watt_df, events_csv_path='./dataframes/house_3_events.csv')
    events_on_day = event_fac.select_events_on_day('03-27')

    patterns = optimization_patterns('C:/Users/Mads/Bachelor/P6/data_analysis/TPM/TPM/output/house_3/Experiment_minsup0.1_minconf_0.1/level2.json')
    patterns_on_day = list(filter(lambda pattern: pattern.date == '03-27', patterns))

    #event_fac.print_events_info()

    #print(len(event_fac.events))
    #filter_level_2_events(event_fac.events, optimization_patterns('./TPM/TPM/output/house3/Experiment_minsup0.1_minconf_0.1/level2.json')) # remove lvl 2 events from lvl 1 list.

    optimizer = Optimizer(house_3_tas)

    cost_before = optimizer.find_total_cost_of_events(events_on_day, price_vector)
    optimizer.optimize_day(events=events_on_day, price_vector=price_vector, patterns=patterns_on_day)
    cost_after = optimizer.find_total_cost_of_events(events_on_day, price_vector)

    print(f'Cost before: {cost_before}\nCost after: {cost_after}\nSavings: {cost_before-cost_after}')

    '''
    print('Before:')
    for event in events_on_day:
        print(event.timeslot)
    optimizer.optimize_day(events=events_on_day, price_vector=price_vector, patterns=patterns_on_day)
    print('After')
    for event in events_on_day:
        print(event.timeslot)
    '''
    



main()

