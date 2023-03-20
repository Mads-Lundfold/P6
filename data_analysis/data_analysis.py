import itertools
from pathlib import Path
import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns
import libs.libraries
from enum import Enum
import numpy as np
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
        "no conversion": None,
        "minutes": 60,
        "5-minutes": 300,
        "quarters": 900,
        "half-hours": 1800,
        "hours": 3600
    }
    if (to == "no conversion"): return time
    minimized_time = math.floor(time / shrinkfactor_dict.get(to))
    return minimized_time * shrinkfactor_dict.get(to)


def write_dataframe_to_csv(dataframe : pd.DataFrame, filename : str) -> None: 
    filepath = Path(f'dataframes/{filename}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    dataframe.to_csv(filepath, index=False, index_label=None, header=False)
    

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
            split_string[0] = convert_seconds_to(int(split_string[0]), 'no conversion')
            split_string[1] = int(split_string[1])
            lines.append(split_string)
    
    return pd.DataFrame(lines, columns=['Time', channel_file.split('/')[-1].rsplit('.', 1)[0]])


def get_data_from_house(house_number : str):
    watt_df = list()

    for file in os.listdir(house_number):
        if (regex.compile("channel_[0-9]+.dat").match(file)):
            # read file from data and return dataframe
            temp = read_entries_from(house_number + '/' + file)
            #temp = read_entries_from_range(50000, 100000, house_number + '/' + file)
            temp = get_average_consumption(temp)
            #join temp on res
            watt_df.append(temp)
    
    watt_df = pd.concat(watt_df, axis=1)
    
    # Uses watt dataframe to create the on/off dataframe.
    on_off_df = apply_power_thresholds(watt_dataframe=watt_df, house_num=house_number.split('/')[-1]).astype(bool)

    return watt_df, on_off_df


def get_temporal_events(on_off_df: pd.DataFrame):
    
    # Initialize list for events
    events = list()

    # Find first day from dataframe
    day_zero = on_off_df.index[0]
    day_zero = datetime.utcfromtimestamp(day_zero)

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
                    'end': next(timestamps, time),
                    'channel': channel,
                    'day': (datetime.utcfromtimestamp(time) - day_zero).days
                })
    
    # Sort events in chronological order
    events = sorted(events, key=lambda x: x['start'])
    return pd.DataFrame(events)

def get_measurement_intervals(channelfile: pd.DataFrame)-> pd.DataFrame:
    df_gaps = channelfile.diff()
    return df_gaps.fillna(0).astype(int)

def draw_histogram_from_list(data: list)-> None:
    return

#def write_list_to_file(list: list)-> None:
#    with open('your_file.txt', 'w') as f:
 #       for line in lines:
 #           f.write(f"{line}\n")

def main():
    #watt_df, on_off_df = get_data_from_house(house_number = house_2)
    df_raw_watt = read_entries_from(channel_file=f"{house_3}/channel_1.dat")
    df_only_time = df_raw_watt.drop(['channel_1'], axis='columns')
    df_only_time = df_only_time.fillna(0)
    df_only_time = df_only_time["Time"].astype(int)
    df_intervals = get_measurement_intervals(df_only_time)
    write_dataframe_to_csv(dataframe=df_raw_watt, filename='df_raw_watt')
    write_dataframe_to_csv(dataframe=df_only_time, filename='df_only_time')
    write_dataframe_to_csv(dataframe=df_intervals, filename='df_intervals')
    
    plt.hist(df_intervals, df_intervals.nunique())
    plt.show()
    print(type(df_intervals))
    print(type(df_raw_watt))
    df_intervals.plot.hist()
    #print(on_off_df)
    #events = get_temporal_events(on_off_df)
    #print(events)
    #write_dataframe_to_csv(events, 'house_2_events')
    #print(watt_df)
    #print(on_off_df)



main()


