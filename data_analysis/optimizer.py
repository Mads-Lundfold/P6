# !!!READ!!! - Entirely unfinished. Lots of thought has been put in, but currently only does the absolute simplest thing it can - it returns the lowest price in a world where everything is hourly and constant.
# Much of the code is junk and has little effect, but the idea was to expand upon it. This should happen soon.

from calendar import timegm
import pandas as pd
import time
from datetime import datetime
from events import FakeDiscreteLvl1Event
from electricity_price_dataset import read_extract_convert_price_dataset

thingy_session = FakeDiscreteLvl1Event(profile = [0.3],
                               units_in_minutes = 60, 
                               maxfreq = 1, 
                               minfreq = 1, 
                               restricted_hours = [(22, 8), (11, 12)],
                               occured=datetime(2015, 11, 20, 18, 0, 0))

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

    price_vector = cut_price_data["GB_GBN_price_day_ahead"].tolist()
    price_vector = list(map(float, price_vector))
    print(price_vector)

    # Perform optimization
        # we need to find a way to map our appliance to a point on the price vector. For now we just place it on the 18th hour.
    previous_cost = event.profile[0]*price_vector[18]
        # Now have current price. Need new price, savings, new time.
        # we will now iterate the simplest way possible. it's all hourly. For now we will even ignore restricted hours.
    lowest_cost = previous_cost
    for timeslot in price_vector:
        if(timeslot*event.profile[0] < lowest_cost): 
            lowest_cost = timeslot*event.profile[0]

    return lowest_cost # needs to return more information - at what time do you get the cost? how expensive was observed use? How much was saved?


start_time = datetime(2015, 11, 20, 0, 0, 0)
end_time = datetime(2015, 11, 21, 0, 0, 0)
df_price = read_extract_convert_price_dataset()
optimize(thingy_session, df_price, start_time, end_time)