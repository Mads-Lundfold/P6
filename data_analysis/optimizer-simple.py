import datetime
import sys
import time
import pandas as pd
import numpy as np
from data_analysis import get_data_from_house

from time_associations import get_quarter_tas
from electricity_price_dataset import read_extract_convert_price_dataset
from event_factory import EventFactory

# Dummy Event class for testing purposes
class Event:
    def __init__(self, appliance, profile, occured) -> None:
        self.appliance = appliance
        self.profile = profile
        self.occured = occured


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
    
    # Handle patterns somehow
    
    def optimize_day(self, events, price_vector):
        # List of the newly scheduled events
        new_schedule = list()
        temp_available_times = self.time_assoications

        for event in events:
            event_len = event.length
            lowest_cost = sys.maxsize # Replace with its current price
            optimal_start = event.occured

            print(event.appliance)
            print(f'Available timeslots for {event.appliance}: \n {temp_available_times[event.appliance]}')

            for i in range(len(price_vector) - event_len):
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

            new_schedule.append(Event(appliance=event.appliance, 
                                      profile=event.profile, 
                                      occured=optimal_start))

        '''
        for event in new_schedule:
            print(event.appliance, event.occured)
        return new_schedule
        '''

    
#len([ele for ele in temp_available_times[event.appliance] if ele < i or ele >= i + event_len])==0


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
    price_vector = np.array(np.repeat(price_data_2015['2015-03-28'],4))
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
    events_on_day = event_fac.select_events_on_day('03-28')

    optimizer = Optimizer(house_3_tas)
    optimizer.optimize_day(events=events_on_day, price_vector=price_vector)
    print(price_vector)


    
def expand_price_vector(price_vector: list, expansion_factor: int) -> list:
    # create new list with each value repeating price_vector many times.
    # now also with an edited time, calculated by increasing successive elements time by expfac/60 many minutes
    expanded_price_vector = list()
    hour = 0
    for price in price_vector:        
        for i in range(expansion_factor):
            new_element = (datetime.time(hour, 15*i), float(price)) # Time vector stuff happens here. Need to increment time with 60/expfactor minutes
            expanded_price_vector.append(new_element)
        hour = hour + 1

    return expanded_price_vector

main()

