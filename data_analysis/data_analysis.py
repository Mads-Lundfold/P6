import itertools
from pathlib import Path
import pandas as pd
import math
import matplotlib.pyplot as plt
#import seaborn as sns
import libs.libraries
from enum import Enum
import numpy as np
import sys
import os
import re as regex
from datetime import datetime
from mlxtend.frequent_patterns import apriori
from typing import List
from collections import Counter

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

def get_unique_elements_from_list(input_list: list)-> list:
    unique_list = []
    for x in input_list:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def get_occurrence_of_element_in_list(input_list: list, element)-> int:
    occurrence = 0
    for x in input_list:
        if x == element: occurrence+=1
    return occurrence


def get_occurrence_of_every_element_in_list(input_list):
    unique_list = get_unique_elements_from_list(input_list)
    occurrence_list = []
    for x in unique_list:
        occurrence_list.append(get_occurrence_of_element_in_list(unique_list, x))
    return unique_list, occurrence_list


def get_unique_elements_from_dataframe(input_frame: pd.DataFrame, column: str)-> np.ndarray:
    unique_array = input_frame[f"{column}"].unique()
    unique_array.sort()
    return unique_array

# Does not do what is supposed!
def get_occurrence_of_elements_in_dataframe(input_frame: pd.DataFrame, column: str)-> pd.DataFrame:
    return input_frame[f'{column}'].value_counts().to_frame()

def get_occurrence_of_every_element_in_dataframe(input_frame: pd.DataFrame, column: str):
    unique_array = get_unique_elements_from_dataframe(input_frame, "Time")
    count_series = pd.Series(dtype=int)
    for x in unique_array:
        count_series.concat()
    return

def add_percentage_column(input_frame: pd.DataFrame)-> pd.DataFrame:
    input_frame['Eng_percent'] = (input_frame['Time'] / 
                      input_frame['Time'].sum()) * 100
    return input_frame

'''
def plot_unique_values_histogram(series: pd.Series)-> None:
    plt.close('all')
    #Right now it puts all the values together in one bar.
    #We want one bar per value
    list_of_uniques = series.tolist()
    print(list_of_uniques)
    np_list_of_uniques = np.array(list_of_uniques)
    #print(len(list_of_uniques))
    bins = np.unique(np_list_of_uniques)
    
    sorted_list = sorted(list_of_uniques)
    sorted_counted = Counter(sorted_list)

    range_length = list(range(max(list_of_uniques))) # Get the largest value to get the range.
    data_series = {}

    for i in range_length:
        data_series[i] = 0 # Initialize series so that we have a template and we just have to fill in the values.

    for key, value in sorted_counted.items():
        data_series[key] = value

    data_series = pd.Series(data_series)
    x_values = data_series.index
    plt.bar(x_values, data_series.values)

    return
'''

def main():
    print("Begin!")
    df_raw_watt = read_entries_from(channel_file=f"{house_5}/channel_4.dat")
    print("Step 2")
    df_only_time = df_raw_watt.drop(['channel_4'], axis='columns')
    print("Step 3")
    df_only_time = df_only_time.fillna(0)
    print("Step 4")
    df_only_time = df_only_time["Time"].astype(int) # Turns into series here!
    print("Step 5")
    df_only_time = df_only_time.to_frame()
    print("Step 6")
    df_intervals = get_measurement_intervals(df_only_time)
    print("Step 7")
    #write_dataframe_to_csv(dataframe=df_raw_watt, filename='df_raw_watt')
    #write_dataframe_to_csv(dataframe=df_only_time, filename='df_only_time')
    #write_dataframe_to_csv(dataframe=df_intervals, filename='df_intervals')

    occurrence_frame = get_occurrence_of_elements_in_dataframe(df_intervals, "Time")
    print("Step 8")
    sorted_occ_frame = occurrence_frame.sort_values(occurrence_frame.columns[0], ascending=False)
    print("Step 9")
    print(sorted_occ_frame)
    print("Step 10")
    sorted_occ_frame_with_percentages = add_percentage_column(sorted_occ_frame)
    print("Step 11")
    sorted_occ_frame_with_percentages.to_csv(path_or_buf="./house_5_channel_4")
    print("Done")




main()


