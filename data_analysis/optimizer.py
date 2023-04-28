# !!!READ!!! - Entirely unfinished. Lots of thought has been put in, but currently only does the absolute simplest thing it can - it returns the lowest price in a world where everything is hourly and constant.
# Much of the code is junk and has little effect, but the idea was to expand upon it. This should happen soon.

# need to modify the algorithm such that each element in cost vector maps to a given time
    # idea: time vector becomes a vector of 2-element tuples: (price, time)

from calendar import timegm
import pandas as pd
import time
from datetime import datetime, timedelta
from events import FakeDiscreteLvl1Event
from electricity_price_dataset import read_extract_convert_price_dataset

HOUR_IN_MINUTES = 60


def optimize(event: FakeDiscreteLvl1Event, price_data: pd.DataFrame, start_time: datetime, end_time: datetime):
    # Cut power data to fit optimization period.
    cut_price_data = price_data[(price_data['unix_timestamp'] >= timegm(start_time.timetuple())) 
                                   & (price_data['unix_timestamp'] < timegm(end_time.timetuple()))]

    # Calculate current costs
    minutes_of_use = len(event.profile) * event.units_in_minutes
        # create a price vector in granularity corresponding to units_in_minutes for the input event. Price vector is delimited by start_time and end_time.
        # Get time delta
    optimization_period = end_time - start_time
        # Get number of units_in_minutes of time delta. - this gives us a length for a price vector from start to end time with units_in_minutes minute units.
    length_of_price_vector = (int(optimization_period.total_seconds())/60)/event.units_in_minutes

    #price_vector = cut_price_data["GB_GBN_price_day_ahead"].tolist()
    #price_vector = list(map(float, price_vector))
    cut_price_data = cut_price_data.astype({'unix_timestamp':'int'})
    cut_price_data = cut_price_data.astype({'GB_GBN_price_day_ahead':'float'})

    # THIS OPERATION MAKES A SERIES!
    cut_price_data['unix_timestamp'] = pd.to_datetime(cut_price_data['unix_timestamp'], unit='s') # makes datetime objects down to second-accuracy.

    price_vector = list(cut_price_data.itertuples(index=False, name = None)) # (datetime,price)
    print(f"Tupled price vector: {price_vector}")
    # Change granularity of price vector
    expansion_factor = calculate_expansion_factor(event.units_in_minutes)
    price_vector = expand_price_vector(price_vector, expansion_factor)
    print(f"Tupled expanded datetimed price vector: {price_vector}")
    exit()

    print(f"lowest element in price vector: {min(price_vector)}")
    print(f"lowest element in price vector times 4: {min(price_vector*4)}")

    # Perform optimization
        # we need to find a way to map our appliance to a point on the price vector. For now we just place it on the 18th hour.
    previous_cost = get_cost_of_single_timeslot(event.profile, price_vector, timeslot_start=10) #TODO timeslot_start is temp bad solution.
    print(f"previous cost {previous_cost}")
        # Now have current price. Need new price, savings, new time.
        # we will now iterate the simplest way possible. it's all hourly. For now we will even ignore restricted hours.
    lowest_cost = previous_cost

#TODO REFACTOR NOW THAT PRICE VECTOR IS TUPLES
    for i in range(len(price_vector)-len(event.profile)):
        new_cost = get_cost_of_single_timeslot(event.profile, price_vector, timeslot_start=i)
        if(new_cost < lowest_cost): 
            lowest_cost = new_cost

    print(f"lowest cost: {lowest_cost}")
    return lowest_cost # needs to return more information - at what time do you get the cost? how expensive was observed use? How much was saved?

def calculate_expansion_factor(event_units_in_minutes):
    expansion_factor = int(HOUR_IN_MINUTES//event_units_in_minutes)
    if (expansion_factor < 1): 
        print("Expansion factor less than 1 in optimize(), exiting.")
        exit(1)
    elif (not(expansion_factor % HOUR_IN_MINUTES)):
        print("Expansion factor not divisible by 60 in optimize, exiting.")
        exit(1)
    return expansion_factor


def expand_price_vector(price_vector: list(), expansion_factor: int) -> list:
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
        

#TODO REFACTOR NOW THAT PRICE VECTOR IS TUPLES
def get_cost_of_single_timeslot(event_profile: list(), price_vector: list(), timeslot_start: int)-> float:
    cost_sum = 0
    i = 0
    for element in event_profile:
        cost_sum = cost_sum + element*price_vector[timeslot_start + i]
        i = i + 1
    return cost_sum


thingy_session = FakeDiscreteLvl1Event(profile = [1, 1, 1, 1, 1],
                               units_in_minutes = 15, 
                               maxfreq = 1, 
                               minfreq = 1, 
                               restricted_hours = [(22, 8), (11, 12)],
                               occured=datetime(2015, 11, 20, 18, 0, 0))

start_time = datetime(2015, 11, 20, 0, 0, 0)
end_time = datetime(2015, 11, 21, 0, 0, 0)
df_price = read_extract_convert_price_dataset()
optimize(thingy_session, df_price, start_time, end_time)