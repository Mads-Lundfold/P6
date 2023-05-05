#TODO: implement restricted/allowed hours
    # Need to incorporate logic to ignore restricted subvectors. (or only select allowed)
    # Need to create event object with time associations
        # imagining lists of delimiting tuples.

#TODO: implement lvl 2 event handling
#TODO: abstract further algorithm details away in implementation detail functions. For instance, lvl 1 opt should probably run again in lvl 2, make function.

from calendar import timegm
import pandas as pd
import time
from datetime import datetime, timedelta
from events import FakeDiscreteLvl1Event, LevelOneEvent
from event_factory import EventFactory, Event
from electricity_price_dataset import read_extract_convert_price_dataset
from data_analysis import get_data_from_house, house_1, house_2, house_3
from datetime import datetime

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


thingy_session = FakeDiscreteLvl1Event(profile = [1, 1, 1, 1, 1],
                               units_in_minutes = 15, 
                               maxfreq = 1, 
                               minfreq = 1, 
                               restricted_hours = [(22, 8), (11, 12)],
                               occured=datetime(2015, 11, 20, 18, 0, 0))

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
events = extract_level_1_events_of_house(3, house3_watt_df)
events = extract_specific_appliance_level_1_events('laptop', events)
start_time = datetime(2013, 3, 25, 0, 0, 0)
end_time = datetime(2013, 3, 26, 0, 0, 0)
events = extract_appliance_level_1_events_within_timeframe(events, start_time, end_time)
print(len(events))



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
print()