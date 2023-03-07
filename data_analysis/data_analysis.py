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
        "half-hours": 1600,
        "hours": 3600
    }
    return math.floor(time / shrinkfactor_dict.get(to))

def write_dataframe_to_csv(dataframe : pd.DataFrame, filename : str) -> None: 
    # TODO
    return
    

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
    result_frame = list()

    for file in os.listdir(house_number):
        if (regex.compile("channel_[0-9]+.dat").match(file)):
            # read file from data and return dataframe
            #temp = read_entries_from(house_number + '/' + file)
            temp = read_entries_from_range(5000, 10000, house_number + '/' + file)
            temp = get_average_consumption(temp)
            #join temp on res
            result_frame.append(temp)
    
    result_frame = pd.concat(result_frame, axis=1)
    return result_frame


def convert_watt_df_to_binary(watt_dataframe : pd.DataFrame):
    watt_dataframe.fillna(0, inplace=True)
    binary_dataframe = watt_dataframe.astype(bool)
    return binary_dataframe


def main():
    watt_house_data = get_data_from_house(house_number = house_2)
    watt_dataframe = apply_power_thresholds(watt_house_data, house_2)
    binary_house_data = convert_watt_df_to_binary(watt_dataframe)
    print(watt_house_data)
    print(watt_dataframe)
    print(binary_house_data)
    #patterns = apriori(binary_house_data, min_support=0.6)
    #print(patterns)



main()


