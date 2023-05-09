import pandas as pd
import sys
import csv
import datetime
from data_analysis import get_data_from_house

class EventFactory:
    def __init__(self, watt_df: pd.DataFrame, events_csv_path: str):
        self.watt_df = watt_df
        self.events_csv_path = events_csv_path
        self.events = self.create_events()


    def create_events(self):
        events = list()
        file = open(self.events_csv_path, "r")
        reader = csv.reader(file)

        # Iterate through each row / event in csv file
        for row in reader:
            # Extract information about event
            start = int(row[0])
            end = int(row[1])
            appliance = row[2]

            # Create event object
            event = Event(appliance = appliance,
                          profile = self.get_profile(start, end, appliance),
                          occured = datetime.datetime.fromtimestamp(start))
                
            events.append(event)
        
        return events

        
    def get_profile(self, start, end, appliance):
        # Select the entries of the full watt df that corresponds to the time span of the event. 
        # This will be the consumption profile for the event.
        profile = self.watt_df[(self.watt_df.index >= start) & (self.watt_df.index < end)]
        profile = profile[appliance]

        # Reset the time index of the event so it start at time 0
        profile.index = profile.index - start

        return profile.tolist()
    
    def select_events_on_day(self, month_day):
        events_on_day = list()
        for event in self.events:
            if event.occured.strftime('%m-%d') == month_day:
                events_on_day.append(event)
        
        return events_on_day
        

    def print_events_info(self):
        for event in self.events:
            print(event.occured)


# Dummy Event class for testing purposes
class Event:
    def __init__(self, appliance, profile, occured) -> None:
        self.appliance = appliance
        self.profile = profile
        self.occured = occured
        self.length = len(profile)


def testspace():
    dataset = str(sys.argv[1])
    house_1 = dataset + "/house_1"
    house_2 = dataset + "/house_2"
    house_3 = dataset + "/house_3"
    house_4 = dataset + "/house_4"
    house_5 = dataset + "/house_5"

    watt_df, on_off_df = get_data_from_house(house_number = house_3) 

    event_fac = EventFactory(watt_df=watt_df, events_csv_path='./dataframes/house_3_events.csv')
    event_fac.print_events_info()

#testspace()