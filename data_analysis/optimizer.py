#REFACTOR NOTES:
    #Events should really store granularity and duration. Would make the rest of the code SO much easier to read and write. 
    #Calculating the duration of events EVERY TIME it's needed somewhere is stupid.
    #There should be a generalized function that just checks if an event is within time. I think it has been programmed 3 slightly different times now!

#Later notes:
#Not really todo for now, but we can try every event once for every appliance, iterating through the time vector at most Max(events of some appliance over that period)

from calendar import timegm
import pandas as pd
import time
import copy
from datetime import datetime, timedelta
from events import FakeDiscreteLvl1Event, LevelOneEvent
from event_factory import EventFactory, Event
from electricity_price_dataset import read_extract_convert_price_dataset
from data_analysis import get_data_from_house, house_1, house_2, house_3
from datetime import datetime
from time_associations import usage_frequencies, get_time_associations

HOUR_IN_MINUTES = 60
TIME = 1
DATETIME = 0
PRICE = 1

#TODO Handle that events of the same appliance should not overlap. (current)
    #Original idea is just a single event, but that can be emulated with a list containing a single event.
    # what if we have a data-structure containing each current placement. Then, if a same-appliance has been placed in the alg, we check to see if we overlap.


def optimize(events: list, time_associations: dict, price_data: pd.DataFrame, start_time: datetime, end_time: datetime, units_in_minutes: int):
    # Copy time_associations into updatable copy that DOES NOT REFER TO THE PREVIOUS
    new_tas = copy.deepcopy(time_associations)
    print("price data?")
    print(price_data)
    # Cut power data to fit optimization period.
    cut_price_data = price_data[(price_data['unix_timestamp'] >= timegm(start_time.timetuple())) 
                                   & (price_data['unix_timestamp'] < timegm(end_time.timetuple()))]
    print(cut_price_data) # FUCKING THING IS EMPTY

    # create a price vector in granularity corresponding to units_in_minutes for the input event. Price vector is delimited by start_time and end_time.
    cut_price_data = cut_price_data.astype({'unix_timestamp':'int'})
    cut_price_data = cut_price_data.astype({'GB_GBN_price_day_ahead':'float'})
    cut_price_data['unix_timestamp'] = pd.to_datetime(cut_price_data['unix_timestamp'], unit='s')
    price_vector = list(cut_price_data.itertuples(index=False, name = None)) # (datetime,price)
    
    # Change granularity of price vector
    expansion_factor = calculate_expansion_factor(units_in_minutes)
    price_vector = expand_price_vector(price_vector, expansion_factor)
    print(price_vector)

    placement_history = dict()

    # Perform optimization (This only happens for a single event profile. That is ok, we now have to place it with the subroutines created.)
    # TODO: Take into account event time associations. 
    # TODO: NEED GET_TIME_ASSOCIATIONS().

    # GET TIME ASSOCIATION FOR event.appliance. Exclude all dicts not of the same kind of appliance.
    # TODO: One event at a time, entire price vector at a time.
    for event in events:
        result = perform_optimization(event, price_vector, new_tas, expansion_factor, placement_history)
        update_placement_history(placement_history, result, minutes_per_unit=units_in_minutes)
    return placement_history

# change alg to loop optimization part for each event, and collect results in a list. We can later iterate over this list to easily determine total savings.

# Takes some event in its time, see if it is contained within all corresponding time pairs.
def events_overlap(placement_history: dict, new_timeslot, event: Event, minutes_per_unit: int)-> bool:
    result = False
    end_timeslot = new_timeslot + minutes_per_unit*len(event.profile)
    for time_interval_tuple in placement_history[event.appliance]:
        if (new_timeslot >= time_interval_tuple[0] and end_timeslot <= time_interval_tuple[1]):
            result = True
            break
    return result


def update_placement_history(placement_history: dict, result: tuple, minutes_per_unit: int)-> None:
    # if dict does not contain key, add key.
    # if dict has key, it has a list. add to the list
    appliance_name = result[4]
    if (not appliance_name in placement_history):
        placement_history[appliance_name] = list()

    # Get duration in 2 datetimes or whatever. Put them in a tuple and append to list.
    start_timestamp = result[3]
    end_timestamp = start_timestamp.minute + minutes_per_unit*len(result[5].profile)
    appendage = (start_timestamp, end_timestamp)
    placement_history[appliance_name].append(appendage)


def perform_optimization(event: Event, price_vector: list, new_tas: dict, expansion_factor: int, placement_history: dict):
    previous_cost = get_cost_of_single_timeslot(event.profile, price_vector, timeslot_start=event.occured)
    lowest_cost = previous_cost

    for i in range(len(price_vector) - len(event.profile)):
        new_timeslot = price_vector[i][TIME]
        if(is_in_TAs(event, new_timeslot, new_tas, expansion_factor) and not events_overlap(placement_history, new_timeslot, event, expansion_factor)):
            new_cost = get_cost_of_single_timeslot(event.profile, price_vector, timeslot_start=new_timeslot)
            if(new_cost < lowest_cost):
                lowest_cost = new_cost
                best_timeslot = new_timeslot

    money_saved = previous_cost-lowest_cost
    return lowest_cost, previous_cost, money_saved, best_timeslot, event.appliance, event #TODO: change this to a struct or something instead of tuple. This is hard to interact with.


def extract_appliance_TAs(appliance: str, time_associations_all: dict)-> list: 
    print(f"time_associations_all: {time_associations_all}")
    return time_associations_all[appliance]


def is_in_TAs(event: Event, new_timeslot, new_tas: dict, expansion_factor: int)->bool:
    result = False
    event_length = len(event.profile)
    start_time = new_timeslot
    minutes_per_unit = expansion_factor
    # Remember: expansion factor is 60/units_in_minutes. 
    end_time = start_time + event_length * timedelta(minutes=minutes_per_unit)

    event_appliance_TAs = extract_appliance_TAs(appliance=event.appliance, time_associations_all=new_tas) # makes list of datetime tuples.
    for time_association in event_appliance_TAs:
        if (start_time.to_pydatetime().time() >= time_association[0] and end_time.to_pydatetime().time() <= time_association[1]): # what is left, what is right? left: <class 'pandas._libs.tslibs.timestamps.Timestamp'>. Right: <class 'datetime.time'>
            result = True
            break

    return result


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
    print(len(price_vector))
    for element in price_vector:
        print(f"{element}, {timeslot_start}")
        if (element[TIME] == timeslot_start): 
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

'''eventfac = EventFactory(house3_watt_df, './dataframes/house_3_events.csv')#'C:/Users/joens/source/repos/P6/data_analysis/dataframes/house_3_events.csv')
house_3_events = eventfac.events
#remove everything but projectors

#for event in house_3_events:
 #   print(event.appliance)

#print(f"events before: {len(house_3_events)}")
list_of_laptop_events = []
for event in house_3_events:
    if (event.appliance) == "laptop": list_of_laptop_events.append(event)

#for event in list_of_laptop_events:
 #   print(datetime.fromtimestamp(event.occured))

# we will optimize day 2013-03-25 11:30:00

start_time = datetime(2013, 3, 25, 0, 0, 0)
end_time = datetime(2013, 3, 26, 0, 0, 0)
df_price = read_extract_convert_price_dataset()


events_within_start_end = filter(lambda event: datetime.fromtimestamp(event.occured) >= start_time and datetime.fromtimestamp(event.occured) <= end_time, list_of_laptop_events)
events_within_start_end = list(events_within_start_end)
print(len(events_within_start_end)) # Vi ser der er 2 laptop events på den givne dag vi kigger på.
'''

def extract_level_1_events_of_house(number: int, house_watt_df: pd.DataFrame)-> list:
    eventfac = EventFactory(house_watt_df, f'./dataframes/house_{number}_events.csv')
    house_events = eventfac.events
    return house_events

# Returns list of events of certain appliance over given time.
def extract_specific_appliance_level_1_events(appliance_name: str, list_of_events: list)-> list: # may need house data as a parameter such that it does not have to be generated every time this is run, better perf.
    list_of_specific_appliance_events = []
    for event in list_of_events: 
        if (event.appliance) == appliance_name: list_of_specific_appliance_events.append(event)
    return list_of_specific_appliance_events

def extract_appliance_level_1_events_within_timeframe(list_of_events: list, start_time: datetime, end_time: datetime)-> list:
    events_within_start_end = filter(lambda event: datetime.fromtimestamp(event.occured) >= start_time and datetime.fromtimestamp(event.occured) <= end_time, list_of_events)
    events_within_start_end = list(events_within_start_end)
    return events_within_start_end

house3_watt_df, on_off_df = get_data_from_house(house_number=house_3)
frequencies = usage_frequencies(on_off_df)
all_time_associations_df, all_time_associations  = get_time_associations(frequencies, f'dataframes/house_{3}_events.csv', 30)

events = extract_level_1_events_of_house(3, house3_watt_df)
events = extract_specific_appliance_level_1_events('laptop', events)
start_time = datetime(2016, 3, 25, 0, 0, 0)
end_time = datetime(2016, 3, 26, 0, 0, 0)
events = extract_appliance_level_1_events_within_timeframe(events, start_time, end_time)
fake_laptop_event = Event(profile=[100, 100, 100, 100, 100], appliance='laptop', occured=datetime(2016, 3, 25, 12, 0, 0))
fake_Event_list = list()
fake_Event_list.append(fake_laptop_event)
res = optimize(events=fake_Event_list, time_associations=all_time_associations, price_data=read_extract_convert_price_dataset(), start_time=start_time, end_time=end_time, units_in_minutes=15)
print(res)


'''
Hvad gøres der ved at de to events ligger på samme dag? Skal måske tænkes over senere...
- Den første skal nok sættes tættest.. aRGH. Svært. Der er nok et aspekt med min-tid og maks-tid.
- Måske skal jeg først tænke på bare at placere dem indenfor den bedste time associated plads, og ignorere at de kan ligge oveni hinanden.
- Som MINIMUM skal de i hvert fald ikke ligge oveni hinanden. Det er ALDRIG muligt, og det skal håndteres.
'''


'''
start_time = datetime(2015, 11, 20, 0, 0, 0)
end_time = datetime(2015, 11, 21, 0, 0, 0)
df_price = read_extract_convert_price_dataset()
optimize(thingy_session, df_price, start_time, end_time)
'''