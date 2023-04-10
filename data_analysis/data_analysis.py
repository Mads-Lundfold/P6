import csv
import collections
import itertools
import json
from pathlib import Path
from types import NoneType
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
from typing import List, Sequence
from os.path import exists
import numpy as np


from power_thresholds import apply_power_thresholds
from appliance_removal import remove_appliances

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
        "none": 1,
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

def write_df_to_csv_detail(dataframe:pd.DataFrame, filename: str, header: bool=False, index: bool=False, index_label: str|NoneType=None)-> None:
    filepath = Path(f'dataframes/{filename}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    dataframe.to_csv(filepath, index=index, index_label=index_label, header=header) 

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


def read_entries_from_time_range(start_time: int, end_time : int, channel_file : str) -> pd.DataFrame:
    df_all_entries = read_entries_from(channel_file, time_shrink_factor="none")
    # drop entries outside of range
    df_entries_in_range = df_all_entries[(df_all_entries['Time'] < start_time) and (df_all_entries['Time'] > end_time)]
    
    return df_entries_in_range


def read_entries_from(channel_file : str, time_shrink_factor: str):
    lines = []

    with open(channel_file) as file:
        for line in file:
            split_string = line.split()
            split_string[0] = convert_seconds_to(int(split_string[0]), time_shrink_factor)
            split_string[1] = int(split_string[1])
            lines.append(split_string)
    
    return pd.DataFrame(lines, columns=['Time', channel_file.split('/')[-1].rsplit('.', 1)[0]])


def get_data_from_house(house_number : str):
    watt_df = list()

    for file in os.listdir(house_number):
        if (regex.compile("channel_[0-9]+.dat").match(file)):
            # read file from data and return dataframe
            temp = read_entries_from(house_number + '/' + file, 'quarters')
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
    

def cut_data_in_time_range(path_events: str, unix_start: str, unix_end: str)-> pd.DataFrame:
    df_events = csv_to_event_df(path_events)
    df_events = df_events[(df_events['start'] >= unix_start) & (df_events['end'] <= unix_end) & (df_events['start'] <= df_events['end'])]
    return df_events

def make_boolean_dataframe_binary(boolean_df: pd.DataFrame)-> None:
    return boolean_df.astype(int)
    #return boolean_df.apply(pd.to_numeric, downcast="signed")

def main():
    watt_df, on_off_df = get_data_from_house(house_number = house_1)   
    #watt_df.to_html('temp.html')
    
    # Remove appliances that are automatically on and therefore cannot be moved
    on_off_df = remove_appliances(on_off_df)
    
    events = get_temporal_events(on_off_df)
    write_dataframe_to_csv(events, 'house_1_events')

    # Print CSV
    '''events_house2_df = pd.read_csv('C:/Users/VikZu/repos/P6/data_analysis/dataframes/house_1_events.csv')
    events_house2_df.to_html('temp.html')'''

    # Print JSON
    '''with open('C:/Users/VikZu/repos/P6/data_analysis/TPM/TPM/output/Experiment_minsup0.6_minconf_0.6/level2.json') as f:
        data = json.load(f)
    
    TPM_df = pd.DataFrame(data)
    TPM_df.to_html('temp.html')'''
#================================================#

def mine_lvl_1_patterns(resultCSV_name: str, house: str) -> None:
    if (not (exists(f'./dataframes/{resultCSV_name}.csv'))) : 
        print("lvl 1 dataframe for house not found. Generating...")
        watt_df, on_off_df = get_data_from_house(house_number = house)
        print("got data from house")
        write_dataframe_to_csv(watt_df, 'house1_watt')
        print("wrote house1_watt")
        write_dataframe_to_csv(watt_df, 'house1_on_off')
        print("wrote house1_on_off")

        binary_on_off_df = make_boolean_dataframe_binary(boolean_df=on_off_df)
        print("got binary on off df")

        write_df_to_csv_detail(binary_on_off_df, resultCSV_name, index=True, index_label="Time", header=True)
        print("wrote binary df to csv")
    print("lvl 1 dataframe for house already found.")
    binary_on_off_df = pd.read_csv(filepath_or_buffer=f'./dataframes/{resultCSV_name}.csv', index_col="Time")
    start_of_2014 = 1388534400 
    start_of_2015 = 1420070400 
    binary_on_off_df= binary_on_off_df.drop(binary_on_off_df.index[np.where(binary_on_off_df.index < start_of_2014)])#[(binary_on_off_df.index >= start_of_2014) & (binary_on_off_df.index < start_of_2015)]
    binary_on_off_df= binary_on_off_df.drop(binary_on_off_df.index[np.where(binary_on_off_df.index >= start_of_2015)])
    print(binary_on_off_df)
    # Create 0-initialized summation dataframe.
    sum_df = pd.DataFrame(0, columns=binary_on_off_df.columns, index=range(96))
    #print(sum_df)

    # Get new df for every day.
    # Add every new temp df to summation frame.
    start = 0
    end = 96
    print(binary_on_off_df.index)
    print("starting to write sum df")
    print(len(binary_on_off_df.index) / 96)
    for _ in range(len(binary_on_off_df.index) / 96):
        temp = binary_on_off_df[start:end]
        sum_df.add(temp) # add temp to sum
        start = start + 96
        end = end + 96

    write_dataframe_to_csv(sum_df, "sum_df")



mine_lvl_1_patterns('lvl1_patterns_house1_timeAndColumns', house_1)

#watt_df, on_off_df = get_data_from_house(house_number = house_1)
#print("got data from house")
#binary_on_off_df = make_boolean_dataframe_binary(boolean_df=on_off_df)
#print("got binary on off df")
#write_dataframe_to_csv(binary_on_off_df, 'binary_on_off_house1_alltime')
#print("wrote binary df to csv")

#boolean_on_off_df = pd.read_csv('./dataframes/binary_on_off_house1_alltime.csv')
#print("loaded boolean dataframe!")
#binary_on_off_df = make_boolean_dataframe_binary(boolean_df=boolean_on_off_df)
#print("boolean dataframe converted to binary dataframe!")
#write_dataframe_to_csv(binary_on_off_df, "binary_on_off_df_house1")
#print("binary dataframe written to csv")

'''
#give quartered data
watt_df, on_off_df = get_data_from_house(house_number = house_1)

# make all data int
on_off_df = on_off_df.apply(pd.to_numeric, downcast="signed")

# Trim away rows outside of desired time range
start_of_2014 = 1388530800
start_of_2015 = 1420066800
on_off_df = on_off_df[start_of_2014:start_of_2015]
#on_off_df = on_off_df[on_off_df["Time"].between(1388530800, 1420066800)] # 2014, 2015 start

# remove top dataframe entries until time is 00:00
    # is this done already?

# Create 0-initialized summation dataframe.
sum_df = pd.DataFrame(0, columns=on_off_df.columns, index=range(96))
print(sum_df)

# Get new df for every day.
# Add every new temp df to summation frame.
start = 0
end = 96
for _ in range(len(on_off_df.index) / 96):
    temp = on_off_df[start:end]
    sum_df.add(temp) # add temp to sum
    start = start + 96
    end = end + 96

write_dataframe_to_csv(sum_df, "sum_df")

print("Done summing level 1 use and writing a frame!")

# create 53 histograms
# TODO

#write_dataframe_to_csv(on_off_df, "on_off_df")
'''


