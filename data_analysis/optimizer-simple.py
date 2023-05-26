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
    
    def __init__(self, time_assoications):
        self.time_associations = time_assoications
    

    def optimize_day_by_consumption(self, events, price_vector, patterns):
        temp_available_times = self.time_associations.copy()
        time_start = 0
        time_end = 95 # hard coded to 15 minute timeslots in 24 hours

        # call level2-filter to get list of lvl2 dicts
        level2 = filter_level_2_events(events,patterns)

        # Sort events so highest consumption is first.
        events.sort(key=lambda e: e.total_consumption, reverse=True)

        # Deconstruct level k patterns to level 2 patterns

        for pattern in level2:
            eventA = pattern['events'][0]
            eventB = pattern['events'][1]
            if pattern['relation'] == '>':
                #print(eventA.appliance, eventA.total_consumption)
                #print(eventB.appliance, eventB.total_consumption)
                #print(f'FOUND CONTAINS PATTERN BETWEEN {eventA.appliance} AND {eventB.appliance}')
                if eventA.total_consumption >= eventB.total_consumption:
                    #print('PLACING A FIRST')
                    self.place_event(eventA, price_vector, temp_available_times, time_start, time_end)
                    self.place_event(eventB, price_vector, temp_available_times, eventA.timeslot, eventA.endslot)
                elif eventA.total_consumption < eventB.total_consumption:
                    #print('PLACING B FIRST')
                    self.place_event(eventB, price_vector, temp_available_times, time_start, time_end)
                    self.place_event(eventA, price_vector, temp_available_times, eventB.timeslot - (eventA.length - eventB.length), eventB.endslot + (eventA.length - eventB.length))
            if pattern['relation'] == '->':
                if eventA.total_consumption >= eventB.total_consumption:
                    self.place_event(eventA, price_vector, temp_available_times, time_start, time_end - eventB.length)
                    self.place_event(eventB, price_vector, temp_available_times, eventA.endslot, time_end)
                elif eventA.total_consumption < eventB.total_consumption:
                    self.place_event(eventB, price_vector, temp_available_times, time_start + eventA.length, time_end)
                    self.place_event(eventA, price_vector, temp_available_times, time_start, eventB.timeslot)
            if pattern['relation'] == '|':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end - pattern['events'][1].length)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].timeslot + 1, pattern['events'][0].endslot + pattern['events'][1].length - 1)

        for event in events:
            self.place_event(event, price_vector, temp_available_times, time_start, time_end)

    def optimize_day_by_duration(self, events, price_vector, patterns):
        # List of the newly scheduled events
        #new_schedule = list()
        temp_available_times = self.time_associations.copy()
        time_start = 0
        time_end = 95 # hard coded to 15 minute timeslots in 24 hours

        
        # call level2-filter to get list of lvl2 dicts
        level2 = filter_level_2_events(events,patterns)
        #print(level2)

        # Sort events so highest consumption is first.
        events.sort(key=lambda e: e.length, reverse=True)

        # Deconstruct level k patterns to level 2 patterns

        for pattern in level2:
            if pattern['relation'] == '>':
                eventA = pattern['events'][0]
                eventB = pattern['events'][1]
                #print(eventA.appliance, eventA.total_consumption)
                #print(eventB.appliance, eventB.total_consumption)
                #print(f'FOUND CONTAINS PATTERN BETWEEN {eventA.appliance} AND {eventB.appliance}')
                if eventA.length >= eventB.length:
                    #print('PLACING A FIRST')
                    self.place_event(eventA, price_vector, temp_available_times, time_start, time_end)
                    self.place_event(eventB, price_vector, temp_available_times, eventA.timeslot, eventA.endslot)
                elif eventA.length < eventB.length:
                    #print('PLACING B FIRST')
                    self.place_event(eventB, price_vector, temp_available_times, time_start, time_end)
                    self.place_event(eventA, price_vector, temp_available_times, eventB.timeslot - (eventA.length - eventB.length), eventB.endslot + (eventA.length - eventB.length))
            if pattern['relation'] == '->':
                if eventA.length >= eventB.length:
                    self.place_event(eventA, price_vector, temp_available_times, time_start, time_end - eventB.length)
                    self.place_event(eventB, price_vector, temp_available_times, eventA.endslot, time_end)
                elif eventA.length < eventB.length:
                    self.place_event(eventB, price_vector, temp_available_times, time_start + eventA.length, time_end)
                    self.place_event(eventA, price_vector, temp_available_times, time_start, eventB.timeslot)
            if pattern['relation'] == '|':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end - pattern['events'][1].length)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].timeslot + 1, pattern['events'][0].endslot + pattern['events'][1].length - 1)

        for event in events:
            self.place_event(event, price_vector, temp_available_times, time_start, time_end)

    
    def optimize_day(self, events, price_vector, patterns):
        # List of the newly scheduled events
        #new_schedule = list()
        temp_available_times = self.time_associations.copy()
        time_start = 0
        time_end = 95 # hard coded to 15 minute timeslots in 24 hours

        # call level2-filter to get list of lvl2 dicts}
        level2 = filter_level_2_events(events,patterns)
        #print(level2)

        # Deconstruct level k patterns to level 2 patterns

        for pattern in level2:
            if pattern['relation'] == '>':
                #print(f"Placing contains between {pattern['events'][0].appliance} and {pattern['events'][1].appliance}")
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].timeslot, pattern['events'][0].endslot)
            if pattern['relation'] == '->':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end - pattern['events'][1].length)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].endslot, time_end)
            if pattern['relation'] == '|':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end - pattern['events'][1].length)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].timeslot + 1, pattern['events'][0].endslot + pattern['events'][1].length - 1)

        for event in events:
            self.place_event(event, price_vector, temp_available_times, time_start, time_end)


    def optimize_day_no_patterns(self, events, price_vector, patterns):
        # List of the newly scheduled events
        #new_schedule = list()
        temp_available_times = self.time_associations.copy()
        time_start = 0
        time_end = len(price_vector) - 1

        for event in events:
            self.place_event(event, price_vector, temp_available_times, time_start, time_end)        
        
    
    def optimize_day_no_tas(self, events, price_vector, patterns):
        # List of the newly scheduled events
        #new_schedule = list()
        temp_available_times = self.time_associations.copy()

        for key in temp_available_times:
            temp_available_times[key] = list(range(0, 95))

        time_start = 0
        time_end = len(price_vector) - 1

        # call level2-filter to get list of lvl2 dicts}
        level2 = filter_level_2_events(events,patterns)

        # Deconstruct level k patterns to level 2 patterns

        for pattern in level2:
            if pattern['relation'] == '>':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].timeslot, pattern['events'][0].endslot)
            if pattern['relation'] == '->':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end - pattern['events'][1].length)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].endslot, time_end)
            if pattern['relation'] == '|':
                self.place_event(pattern['events'][0], price_vector, temp_available_times, time_start, time_end - pattern['events'][1].length)
                self.place_event(pattern['events'][1], price_vector, temp_available_times, pattern['events'][0].timeslot + 1, pattern['events'][0].endslot + pattern['events'][1].length - 1)

        for event in events:
            self.place_event(event, price_vector, temp_available_times, time_start, time_end)  



    def optimize_day_no_patterns_no_tas(self, events, price_vector, patterns):
        # List of the newly scheduled events
        #new_schedule = list()
        temp_available_times = self.time_associations.copy()

        for key in temp_available_times:
            temp_available_times[key] = list(range(0, 95))

        time_start = 0
        time_end = len(price_vector) - 1

        for event in events:
            self.place_event(event, price_vector, temp_available_times, time_start, time_end)  



    def place_event(self, event: Event, price_vector: list, temp_available_times: dict, start_time: int, end_time: int):
        if event.placed:
            return 
        #print(f'Timespan for {event.appliance} with length {event.length}: {start_time} - {end_time}')

        event_len = event.length
        lowest_cost = np.sum(event.profile * price_vector[event.timeslot:event.timeslot+event_len])
        optimal_start = event.timeslot

        #print(event.appliance)
        #print(f'Available timeslots for {event.appliance}: \n {temp_available_times[event.appliance]}')

        for i in range(start_time, end_time - event_len + 1):
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
        #print(f'Timeslots where {event.appliance} has been placed: {taken_slots}')

        event.timeslot = optimal_start
        event.endslot = event.timeslot + event.length
        event.placed = True
        

    def find_total_cost_of_events(self, events: list, price_vector: list):
        total_cost = 0
        for event in events:
            try:
                cost = np.sum(event.profile * price_vector[event.timeslot : event.timeslot+event.length])
                total_cost = total_cost + cost
            except ValueError:
                print(f"{event.appliance} lasted more than 2 days, therefore couldn't be calculated")
        return total_cost

    


def create_price_vector_dataset(start: int, end: int):
    price_data = read_extract_convert_price_dataset()
    price_data_2015 = price_data[price_data['unix_timestamp'].between(start, end)]

    price_data_2015['unix_timestamp'] = pd.to_datetime(price_data_2015['unix_timestamp'], unit='s').dt.strftime('%Y-%m-%d')

    price_data_2015 = price_data_2015.groupby('unix_timestamp')['GB_GBN_price_day_ahead'].apply(list)
    #print(price_data_2015)

    return price_data_2015


def main():
    # Get price data
    price_data_2015 = create_price_vector_dataset(1420066800, 1451602800)

    # Get events for house
    watt_df = pd.read_csv('./dataframes/house_1_2014_15min_watts.csv').set_index('Time')
    print(watt_df)

    event_fac = EventFactory(watt_df=watt_df, events_csv_path='./dataframes/house_1_2014.csv')

    # Get patterns for house
    patterns = optimization_patterns('./TPM/TPM/output/Experiment_minsup0.15_minconf_0.6/level2.json')

    # Get time associations
    house_tas = get_quarter_tas()    

    optimizer = Optimizer(house_tas)

    # Optimize
    # Create cost before and after optimization
    total_cost_before = 0
    total_cost_after = 0

    # Optimize over multiple days in time range, on a daily basis
    day_range = pd.date_range(start='1/2/2014', end='12/30/2014')
    for i in day_range:
        day = i.date().strftime('%m-%d')
        next_day = (i.date() + datetime.timedelta(days=1)).strftime('%m-%d')
        
        price_vector = price_data_2015['2015-' + day]
        price_vector = np.array(np.repeat(price_vector,4))
        
        next_day_price_vector = price_data_2015['2015-' + next_day]
        next_day_price_vector = np.array(np.repeat(next_day_price_vector,4))

        events_on_day = event_fac.select_events_on_day(day)
        patterns_on_day = list(filter(lambda pattern: pattern.date == day, patterns))

        # Use total_cost_before to calculate total cost before optimization - a baseline. 
        total_cost_before = total_cost_before + optimizer.find_total_cost_of_events(events_on_day, np.append(price_vector, next_day_price_vector))
        cost_before = optimizer.find_total_cost_of_events(events_on_day, np.append(price_vector, next_day_price_vector))
        optimizer.optimize_day(events=events_on_day, price_vector=np.append(price_vector, next_day_price_vector), patterns=patterns_on_day)
        #optimizer.optimize_day_no_patterns_no_tas(events=events_on_day, price_vector=price_vector, patterns=patterns_on_day)
        total_cost_after = total_cost_after + optimizer.find_total_cost_of_events(events_on_day, np.append(price_vector, next_day_price_vector))
        
        #print(f"{day} - Today's savings {cost_before - optimizer.find_total_cost_of_events(events_on_day, np.append(price_vector, next_day_price_vector))}, overall savings {total_cost_before - total_cost_after}, first price {price_vector[0]}")
        
        
    print(f'Cost before: {total_cost_before}\nCost after: {total_cost_after}\nSavings: {total_cost_before-total_cost_after}')

    

main()
