import pandas as pd
import numpy as np

from time_associations import get_restricted_times
from electricity_price_dataset import read_extract_convert_price_dataset

# Dummy Event class for testing purposes
class Event:
    def __init__(self, appliance, profile, occured) -> None:
        self.appliance = appliance
        self.profile = profile
        self.occured = occured


class Optimizer:
    def __init__(self, events: Event, price_data, restricted_times, patterns):
        self.events = events
        self.price_data = price_data
        self.restricted_times = restricted_times
        self.patterns = patterns
    
    
    def optimize_day(self, events, price_vector):
        # List of the newly scheduled events
        new_schedule = list(Event)
        temp_restricted_times = self.restricted_times

        for event in events:
            event_len = len(event.profile)
            lowest_cost = np.sum(event.profile * price_vector[0:event_len])
            optimal_start = 0

            for i in range(len(price_vector) - event_len):
                new_cost = np.sum(event * price_vector[i:i+event_len])
                if new_cost < lowest_cost:
                    lowest_cost = new_cost
                    optimal_start = i
            
            temp_restricted_times[event.appliance] += [i, i+event_len]
            new_schedule.append(Event(appliance=event.appliance, 
                                      profile=event.profile, 
                                      occured=optimal_start))

        return new_schedule

    def place_event(event: Event, ):
        return True
    
    

def main():
    #house_3_restricted_times = get_restricted_times()
    #print(house_3_restricted_times)
    price_data = read_extract_convert_price_dataset()
    start = 1420066800
    end = 1451602800
    price_data_2015 = price_data[price_data['unix_timestamp'].between(start, end)]

    price_data_2015['unix_timestamp'] = pd.to_datetime(price_data_2015['unix_timestamp'], unit='s').dt.strftime('%Y:%m:%d')
    print(price_data_2015)

    price_data_2015 = price_data_2015.groupby(price_data_2015['unix_timestamp'])



main()

  
  