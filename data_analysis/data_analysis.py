import csv
import collections
import itertools
import json
from pathlib import Path
import pandas as pd
import math
import matplotlib.pyplot as plt
import libs.libraries
from enum import Enum
import sys
import os
import re as regex
from datetime import datetime
from mlxtend.frequent_patterns import apriori
from typing import List

from power_thresholds import apply_power_thresholds

#TODO better data access solution
#TODO refactoring of tools and helper functions into library package

#TODO data-analysis with tools (mby)
#TODO data mining libs
#TODO data mining research

#make variable string
dataset = str(sys.argv[1])
house_1 = dataset + "/house_1"
house_2 = dataset + "/house_2"
house_3 = dataset + "/house_3"
house_4 = dataset + "/house_4"
house_5 = dataset + "/house_5"

# find filer med channel_(int) i regex

def convert_seconds_to(time : int, to : str) -> int: 
    shrinkfactor_dict = {
        "minutes": 60,
        "5-minutes": 300,
        "quarters": 900,
        "half-hours": 1800,
        "hours": 3600
    }
    minimized_time = math.floor(time / shrinkfactor_dict.get(to))
    return minimized_time * shrinkfactor_dict.get(to)


def write_dataframe_to_csv(dataframe : pd.DataFrame, filename : str) -> None: 
    filepath = Path(f'dataframes/{filename}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    dataframe.to_csv(filepath, index=False, index_label=None, header=False)
    

def csv_to_event_df(csv_path: str):
    file = open(csv_path, "r")
    events = list(csv.reader(file, delimiter=","))
    events_df = pd.DataFrame(events, columns=['start', 'end', 'appliance', 'day'])

    return events_df


def get_average_consumption(entries_in_seconds : pd.DataFrame) -> pd.DataFrame:
    return entries_in_seconds.groupby('Time').mean()


def plot_power_usage(dataframe : pd.DataFrame) -> None:
    dataframe.plot()
    plt.show()


def read_entries_from_range(start: int, end : int, channel_file : str) -> pd.DataFrame:
    # TODO : Refactor this code
    lines = []

    with open(channel_file) as data:
        for line in itertools.islice(data, start, end):
            split_string = line.split()
            split_string[0] = convert_seconds_to(int(split_string[0]), 'quarters')
            split_string[1] = int(split_string[1])
            lines.append(split_string)
        
    return pd.DataFrame(lines, columns=['Time', channel_file.split('/')[-1].rsplit('.', 1)[0]])


def read_entries_from(channel_file : str):
    lines = []

    with open(channel_file) as file:
        for line in file:
            split_string = line.split()
            split_string[0] = convert_seconds_to(int(split_string[0]), 'quarters')
            split_string[1] = int(split_string[1])
            lines.append(split_string)
    
    return pd.DataFrame(lines, columns=['Time', channel_file.split('/')[-1].rsplit('.', 1)[0]])


def get_data_from_house(house_number : str):
    watt_df = list()

    for file in os.listdir(house_number):
        if (regex.compile("channel_[0-9]+.dat").match(file)):
            # read file from data and return dataframe
            temp = read_entries_from(house_number + '/' + file)
            #temp = read_entries_from_range(100000, 300000, house_number + '/' + file)
            temp = get_average_consumption(temp)
            #join temp on res
            watt_df.append(temp)
    
    watt_df = pd.concat(watt_df, axis=1)

    # Uses watt dataframe to create the on/off dataframe.
    on_off_df = apply_power_thresholds(watt_dataframe=watt_df, house_num=house_number.split('/')[-1]).astype(bool)

    label_dictionary = create_label_dictionary(house_number + '/labels.dat')
    
    watt_df = watt_df.rename(columns=label_dictionary)
    on_off_df = on_off_df.rename(columns=label_dictionary)

    return watt_df, on_off_df


def get_temporal_events(on_off_df: pd.DataFrame):
    
    # Initialize list for events
    events = list()

    # Find first day from dataframe
    day_zero = on_off_df.index[0]
    day_zero = datetime.utcfromtimestamp(day_zero)

    # Find the last timestamp in the dataframe
    end_time = on_off_df.index[-1]

    # Iterate through each channel of the dataframe
    for channel in on_off_df.columns:

        # Check if the channel gets turned on/off between following timestamps
        # If it does, save the time where it changes
        status_changes = on_off_df[channel].where(on_off_df[channel] != on_off_df[channel].shift(1)).dropna()

        # Create an iterable out of the timestamps
        timestamps = iter(status_changes.index.tolist())

        # Create an event for each change where the channel was turned on
        for time in timestamps:
            if status_changes[time] == True:
                events.append({
                    'start': time,
                    'end': next(timestamps, end_time),
                    'channel': channel,
                    'day': (datetime.utcfromtimestamp(time) - day_zero).days
                })
    
    # Sort events in chronological order
    events = sorted(events, key=lambda x: x['start'])
    return pd.DataFrame(events)


def create_label_dictionary(labels_path : str):
    # Read the labels.dat into a dictionary <channel #> : <appliance>
    labels_dict = {}
    with open(labels_path, 'r') as f:
        for line in f:
            line = line.strip().split()
            labels_dict[f"channel_{line[0]}"] = line[1]
    return labels_dict


def event_duration_analysis(csv_path: str):
    
    # Load events from csv file
    events_df = csv_to_event_df(csv_path)

    # Calculate the duration of each event, and make a list for each appliance of its events' durations.
    events_df['duration'] = (events_df['end'].astype('int') - events_df['start'].astype('int'))
    events_df.drop(columns=['start', 'end', 'day'], inplace=True)
    
    durations = events_df.groupby('appliance')['duration'].apply(list)

    print(durations)
    

    


def main():
    watt_df, on_off_df = get_data_from_house(house_number = house_2)   
    #watt_df.to_html('temp.html')
    
    events = get_temporal_events(on_off_df)
    write_dataframe_to_csv(events, 'house_2_events')
    

main()



