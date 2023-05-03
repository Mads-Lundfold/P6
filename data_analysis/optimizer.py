#TODO: implement restricted/allowed hours
#TODO: implement lvl 2 event handling
#TODO: abstract further algorithm details away in implementation detail functions. For instance, lvl 1 opt should probably run again in lvl 2, make function.

from calendar import timegm
import pandas as pd
import time
from datetime import datetime, timedelta
from events import FakeDiscreteLvl1Event
from electricity_price_dataset import read_extract_convert_price_dataset
import numpy as np

HOUR_IN_MINUTES = 60


def optimize(event: FakeDiscreteLvl1Event, price_data: pd.DataFrame, start_time: datetime, end_time: datetime):
    # Cut power data to fit optimization period.
    cut_price_data = price_data[(price_data['unix_timestamp'] >= timegm(start_time.timetuple())) 
                                   & (price_data['unix_timestamp'] < timegm(end_time.timetuple()))]

    # create a price vector in granularity corresponding to units_in_minutes for the input event. Price vector is delimited by start_time and end_time.
    cut_price_data = cut_price_data.astype({'unix_timestamp':'int'})
    cut_price_data = cut_price_data.astype({'GB_GBN_price_day_ahead':'float'})
    cut_price_data['unix_timestamp'] = pd.to_datetime(cut_price_data['unix_timestamp'], unit='s')
    price_vector = list(cut_price_data.itertuples(index=False, name = None)) # (datetime,price)
    
    # Change granularity of price vector
    expansion_factor = calculate_expansion_factor(event.units_in_minutes)
    price_vector = expand_price_vector(price_vector, expansion_factor)

    # Perform optimization
    previous_cost = get_cost_of_single_timeslot(event.profile, price_vector, timeslot_start=event.occured)
    lowest_cost = previous_cost

    for i in range(len(price_vector) - len(event.profile)):
        new_timeslot = price_vector[i][1]
        new_cost = get_cost_of_single_timeslot(event.profile, price_vector, timeslot_start=new_timeslot)
        if(new_cost < lowest_cost): 
            lowest_cost = new_cost
            best_timeslot = new_timeslot

    money_saved = previous_cost-lowest_cost
    return lowest_cost, previous_cost, money_saved, best_timeslot

def calculate_expansion_factor(event_units_in_minutes):
    expansion_factor = int(HOUR_IN_MINUTES//event_units_in_minutes)
    if (expansion_factor < 1): 
        print("Expansion factor less than 1 in optimize(), exiting.")
        exit(1)
    elif (not(expansion_factor % HOUR_IN_MINUTES)):
        print("Expansion factor not divisible by 60 in optimize, exiting.")
        exit(1)
    return expansion_factor


def expand_price_vector(price_vector: list, expansion_factor: int) -> list:
    # create new list with each value repeating price_vector many times.
    # now also with an edited time, calculated by increasing successive elements time by expfac/60 many minutes
    expanded_price_vector = list()
    for element in price_vector:
        i = 0        
        for _ in range(expansion_factor):
            new_element = (element[1], element[0] + timedelta(minutes=int(HOUR_IN_MINUTES/expansion_factor)) * i) # Time vector stuff happens here. Need to increment time with 60/expfactor minutes
            expanded_price_vector.append(new_element)
            i = i + 1

    return expanded_price_vector
        

def get_cost_of_single_timeslot(event_profile: list, price_vector: list, timeslot_start: datetime)-> float:
    cost_sum = 0
    #Find start element of interest
    for element in price_vector:
        if (element[1] == timeslot_start): 
            first_corresponding_element_index = price_vector.index(element)
            break
    #Sum operations
    i = 0
    for element in range(first_corresponding_element_index, first_corresponding_element_index+len(event_profile)): 
        cost_sum += event_profile[i] * price_vector[element][0]
        i+=1

    print(f"index: {first_corresponding_element_index}")
    print(f"summed cost: {cost_sum}")

    return cost_sum

# Test for placing two events. Place first event first, then place second event after.
def test(event1: FakeDiscreteLvl1Event, event2: FakeDiscreteLvl1Event, price_data: pd.DataFrame, start_time: datetime, end_time: datetime):
    # Get price data within time span
    cut_price_data = price_data[(price_data['unix_timestamp'] >= timegm(start_time.timetuple())) 
                                   & (price_data['unix_timestamp'] < timegm(end_time.timetuple()))]

    # Expand price data to have same granularity as events (15 miinutes)
    price_vector = cut_price_data['GB_GBN_price_day_ahead'].tolist()
    price_vector = np.array(np.repeat(price_vector,4))
    price_vector = price_vector.astype('float64')

    # Get length of event
    event1_length = len(event1.profile)

    # Find best placement for event 1
    lowest_cost = np.sum(event1.profile * price_vector[0:event1_length])
    optimal_start = 0
    
    for i in range(len(price_vector)-event1_length):
        new_cost = np.sum(event1.profile * price_vector[i:i+event1_length])
        if new_cost < lowest_cost:
            lowest_cost = new_cost
            optimal_start = i

    # Find best placement for event 2
    event2_length = len(event2.profile)
    lowest_event2_cost = np.sum(event2.profile * price_vector[optimal_start:optimal_start+event2_length])
    event2_start = optimal_start

    for i in range(optimal_start, optimal_start+event1_length):
        new_event2_cost = np.sum(event2.profile * price_vector[i:i+event2_length])
        if new_event2_cost < lowest_event2_cost:
            lowest_event2_cost = new_event2_cost
            event2_start = i


    print(f"lowest cost for event 1: {lowest_cost}")
    print(f"lowest cost for event 2: {lowest_event2_cost}")
    print(f"total cost: {lowest_cost + lowest_event2_cost}")
    print(f"event 1 start time: {optimal_start}")
    print(f"event 2 start time: {event2_start}")
    return lowest_cost


# Combine the two profiles by placing the most consuming parts at the same time.
def combine_contains_pattern(outer: FakeDiscreteLvl1Event, inner: FakeDiscreteLvl1Event):
    inner_length = len(inner.profile)
    outer_length = len(outer.profile)
    highest_consumption = np.sum(inner.profile + outer.profile[0:inner_length])
    delay = 0

    for i in range(0, outer_length - inner_length):
        temp_consumption = np.sum(inner.profile + outer.profile[i:i+inner_length])
        if temp_consumption > highest_consumption:
            highest_consumption = temp_consumption
            delay = i
    

    combined_event = np.copy(outer.profile)
    for i in range(delay, delay + inner_length):
        combined_event[i] = combined_event[i] + inner.profile[i - delay]

    '''
    print(highest_consumption)
    print(delay)

    print(outer.profile)
    print(inner.profile)
    print(combined_event)
    '''
    return combined_event

# Place a combined event as you would will a level 1 event
def test2(event1, price_data: pd.DataFrame, start_time: datetime, end_time: datetime):
    # Get price data within time span
    cut_price_data = price_data[(price_data['unix_timestamp'] >= timegm(start_time.timetuple())) 
                                   & (price_data['unix_timestamp'] < timegm(end_time.timetuple()))]

    # Expand price data to have same granularity as events (15 miinutes)
    price_vector = cut_price_data['GB_GBN_price_day_ahead'].tolist()
    price_vector = np.array(np.repeat(price_vector,4))
    price_vector = price_vector.astype('float64')

    # Get length of event
    event1_length = len(event1)

    # Find best placement for event 1
    lowest_cost = np.sum(event1 * price_vector[0:event1_length])
    optimal_start = 0
    
    for i in range(len(price_vector)-event1_length):
        new_cost = np.sum(event1 * price_vector[i:i+event1_length])
        if new_cost < lowest_cost:
            lowest_cost = new_cost
            optimal_start = i
    
    print(f"total cost: {lowest_cost}")
    print(f"Combined event start time: {optimal_start}")


thingy_session = FakeDiscreteLvl1Event(profile = np.array([200, 300, 100, 176, 115, 3728, 46274, 99]),
                               units_in_minutes = 15, 
                               maxfreq = 1, 
                               minfreq = 1, 
                               restricted_hours = [(22, 8), (11, 12)],
                               occured=datetime(2015, 11, 20, 18, 0, 0))

smaller_thingy_session = FakeDiscreteLvl1Event(profile = [893, 2746, 100, 3739, 100],
                               units_in_minutes = 15, 
                               maxfreq = 1, 
                               minfreq = 1, 
                               restricted_hours = [(22, 8), (11, 12)],
                               occured=datetime(2015, 11, 20, 18, 0, 0))

start_time = datetime(2015, 11, 20, 0, 0, 0)
end_time = datetime(2015, 11, 21, 0, 0, 0)
df_price = read_extract_convert_price_dataset()
print('Place first event first, place second after:')
test(thingy_session, smaller_thingy_session, df_price, start_time, end_time)
print('Combine events first, place total event:')
combined_event = combine_contains_pattern(thingy_session, smaller_thingy_session)
test2(combined_event, df_price, start_time, end_time)