#TODO: implement restricted/allowed hours
    # Need to incorporate logic to ignore restricted subvectors. (or only select allowed)
    # Need to create event object with time associations
        # imagining lists of delimiting tuples.

#TODO: implement lvl 2 event handling
#TODO: abstract further algorithm details away in implementation detail functions. For instance, lvl 1 opt should probably run again in lvl 2, make function.

#TODO CURRENT: Optimize an event for one day such that it fits the right spot that day.

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

#TODO definere hvad algoritmen i det hele skal. Lige nu tager den bare en decideret event, men det er måske bare fint.
    # Så kan man cycle gennem en liste af events, det er måske heller ikke så galt. MEN SÅ KAN MAN JO IKKE HOLDE STYR PÅ HVOR TING PLACERES! Det dur ikke.
    # Hold styr på det med ekstern pris-vektor som har tredje element, available: bool, 
        # Ok, men indtil videre så tager vi bare og lader events blive placeret oveni hinanden. Vi napper bare den ene laptop event og kalder det en dag.


#TODO the algorithm should take a single appliance and try every time slot(in TAs)
#TODO not really todo for now, but we can try every event once for every appliance, iterating through the time vector at most max (events of some appliance over that period)




def optimize(event: Event, time_associations: dict, price_data: pd.DataFrame, start_time: datetime, end_time: datetime, units_in_minutes: int):
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

    # Perform optimization (This only happens for a single event profile. That is ok, we now have to place it with the subroutines created.)
    # TODO: Take into account event time associations. 
    # TODO: NEED GET_TIME_ASSOCIATIONS().

    # GET TIME ASSOCIATION FOR event.appliance. Exclude all dicts not of the same kind of appliance.
    # TODO: One event at a time, entire price vector at a time.

    previous_cost = get_cost_of_single_timeslot(event.profile, price_vector, timeslot_start=event.occured)
    lowest_cost = previous_cost

    for i in range(len(price_vector) - len(event.profile)):
        new_timeslot = price_vector[i][TIME]
        if(is_in_TAs(event, new_timeslot, new_tas, expansion_factor)):
            new_cost = get_cost_of_single_timeslot(event.profile, price_vector, timeslot_start=new_timeslot)
            if(new_cost < lowest_cost):
                lowest_cost = new_cost
                best_timeslot = new_timeslot

    money_saved = previous_cost-lowest_cost
    return lowest_cost, previous_cost, money_saved, best_timeslot


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
        print(type(start_time))
        print(type(time_association[0]))
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
res = optimize(event=fake_laptop_event, time_associations=all_time_associations, price_data=read_extract_convert_price_dataset(), start_time=start_time, end_time=end_time, units_in_minutes=15)
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