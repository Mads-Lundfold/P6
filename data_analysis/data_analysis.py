import itertools
import pandas as pd
import math
import matplotlib.pyplot as plt
import libs.libraries
from enum import Enum
import sys
import os
import re as regex
from mlxtend.frequent_patterns import apriori
from typing import List
from pathlib import Path

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
        "6-seconds": 1,
        "minutes": 60,
        "5-minutes": 300,
        "quarters": 900,
        "half-hours": 1600,
        "hours": 3600
    }
    return math.floor(time / shrinkfactor_dict.get(to))


def write_dataframe_to_csv(dataframe : pd.DataFrame, filename : str) -> None: 
    filepath = Path(f'dataframes/{filename}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    dataframe.to_csv(filepath)
    

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


def channel_to_df_in_seconds(channel_file : str) -> pd.DataFrame:
    # TODO : Refactor this code
    lines = []

    with open(channel_file) as data:
        for line in itertools.islice(data, None):
            split_string = line.split()
            split_string[0] = int(split_string[0])
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
    result_frame = list()

    for file in os.listdir(house_number):
        if (regex.compile("channel_[0-9]+.dat").match(file)):
            # read file from data and return dataframe
            #temp = read_entries_from(house_number + '/' + file)
            temp = read_entries_from_range(9000, 12000, house_number + '/' + file)
            temp = get_average_consumption(temp)
            #join temp on res
            result_frame.append(temp)
    
    result_frame = pd.concat(result_frame, axis=1)
    return result_frame


def convert_watt_df_to_binary(watt_dataframe : pd.DataFrame):
    watt_dataframe.fillna(0, inplace=True)
    binary_dataframe = watt_dataframe.astype(bool)
    return binary_dataframe

# IDÉ: LAV ET KOMPLET FRAME OG BARE JOIN!
# Get difference in time values to: see how many rows to add AND: if their value will be 0 or previous
def plug_channel_holes(df_channel: pd.DataFrame, house: str,channel: int)-> pd.DataFrame:
    channelFile = f'{house}/channel_{channel}.dat'
    num_lines = sum(1 for line in open(channelFile))-1 #-1 because last line in file is empty
    # get duration of measurement
    firstSecond = df_channel.at[0, "Time"]
    lastSecond = df_channel.at[num_lines, "Time"]
    #lastSecond = df_channel[num_lines,0] # error
    
    seconds_transpired = lastSecond - firstSecond
    #df_dummy = pd.DataFrame(index=seconds_transpired/6, columns=df_channel.columns)

    for row in range(0, num_lines): 
        prev = int(df_channel._get_value(row, "Time"))
        if prev:
            next = int(df_channel._get_value(row+1, "Time"))
            difference = abs(prev-next)
            if (difference > 6):
                rows_to_add = (difference/6)-1
                if (difference >= 60):
                    # add 0-watt-rows
                    print("hi daddy! :D")

                else: 
                    # add prev-rows
                    print("Hi mommy! :D")
    print("firstsecond = ", firstSecond)
    print("lastsecond = ", lastSecond)
    print("seconds transpired = ", seconds_transpired)
    print("measurements in file: ", num_lines)
    print("required measurements in that timeframe:", seconds_transpired/6)
    return df_channel # IMPROMPTU, CHANGE!
    '''
    for row in df_channel: # det er ikke måden!
        prev = int(df_channel[row, 0])
        next = int(df_channel[row+1, 0])
        difference = abs(prev-next)
        if (difference > 6):
            rows_to_add = difference/6
            if (difference >= 60):
                # add 0-rows
            else: 
                # add prev-rows'''

    # make dummy dataframe
    #df_dummy = pd.DataFrame(index=seconds_transpired/6, columns=df_channel.columns)
    # merge frames on time
    # 

    #new new plan: fill dummy data frame of right size with necessary rows by iterating over the 
    #channel frame



def clean_channel(house: str, channel: int)-> None:
    channelFile = f'{house}/channel_{channel}.dat' # locate file
    df_channel = channel_to_df_in_seconds(channelFile) # make dataframe
    df_plugged = plug_channel_holes(df_channel, house, 1)
    write_dataframe_to_csv(df_plugged, "test_channel_cleaning")# write csv

def main():
    #watt_house_data = get_data_from_house(house_number = house_1)
    #binary_house_data = convert_watt_df_to_binary(watt_house_data)
    #print(watt_house_data)
    #print(binary_house_data)
    #patterns = apriori(binary_house_data, min_support=0.2)
    #print(patterns)
    #channel_df = read_entries_from(f'{house_3}')
    clean_channel(house_3, channel=1)



main()


