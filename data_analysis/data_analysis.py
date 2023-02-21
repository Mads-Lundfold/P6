import pandas as pd
import math
import matplotlib.pyplot as plt
import libs.libraries
from enum import Enum

data_location = 'D:/unidata/data.ukedc.rl.ac.uk/browse/edc/efficiency/residential/EnergyConsumption/Domestic/UK-DALE-2017/UK-DALE-FULL-disaggregated/ukdale'
# contains house 1-5 + metadata folder.
house1_channel_2 = 'D:/unidata/data.ukedc.rl.ac.uk/browse/edc/efficiency/residential/EnergyConsumption/Domestic/UK-DALE-2017/UK-DALE-FULL-disaggregated/ukdale/house_1/channel_2.dat'
house1_channel_5 = 'D:/unidata/data.ukedc.rl.ac.uk/browse/edc/efficiency/residential/EnergyConsumption/Domestic/UK-DALE-2017/UK-DALE-FULL-disaggregated/ukdale/house_1/channel_5.dat'
house1_channel_4 = 'D:/unidata/data.ukedc.rl.ac.uk/browse/edc/efficiency/residential/EnergyConsumption/Domestic/UK-DALE-2017/UK-DALE-FULL-disaggregated/ukdale/house_1/channel_4.dat'
house1_channel_6 = 'D:/unidata/data.ukedc.rl.ac.uk/browse/edc/efficiency/residential/EnergyConsumption/Domestic/UK-DALE-2017/UK-DALE-FULL-disaggregated/ukdale/house_1/channel_6.dat'
house1_channel_7 = 'D:/unidata/data.ukedc.rl.ac.uk/browse/edc/efficiency/residential/EnergyConsumption/Domestic/UK-DALE-2017/UK-DALE-FULL-disaggregated/ukdale/house_1/channel_7.dat'
#Read disaggregated data

def seconds_to(unit : str, unix_seconds : int) -> int: 
    shrinkfactor_dict = {
        "minutes": 60,
        "5-minutes": 300,
        "quarters": 900,
        "half-hours": 1600,
        "hours": 3600
    }
    return unix_seconds/shrinkfactor_dict.get(unit)

def write_dataframe_to_csv(dataframe : pd.DataFrame, filename : str) -> None: 
    return
    #todo 

def unix_secs_to_unix_mins(unix_time : int) -> int: 
    return math.floor(unix_time / 60)

def unix_secs_to_fifteen_min(unix_time : int): return math.floor(unix_time / 900)

# Full outer join on two appliance dataframes
def combine_dataframes(df1 : pd.DataFrame, df2 : pd.DataFrame) -> pd.DataFrame:
    df3 = pd.merge(df1, df2, how='outer', on='Time') 
    return df3


def read_x_entries(x : int, channel_file : str) -> pd.DataFrame:
    # TODO : Refactor this code
    lines = []

    with open(channel_file) as data:
        for _ in range(x):
            line = next(data).split()
            line[0] = (unix_secs_to_unix_mins(int(line[0]))) # Does 2 things at once! calculates and converts from string to int.
            line[1] = int(line[1])
            lines.append(line)
    
    return pd.DataFrame(lines, columns=['Time', 'Power'])
 

def get_average_minute_consum(entries_in_seconds : pd.DataFrame) -> pd.DataFrame:
    return entries_in_seconds.groupby('Time').mean()

def plot_power_usage(dataframe : pd.DataFrame) -> None:
     
    dataframe.plot.bar()
    dataframe.plot()
    plt.show()

def main():
    data = read_x_entries(1000, house1_channel_4)
    minute_data = get_average_minute_consum(data)
    #minute_data_2 = get_average_minute_consum(read_x_entries(1000, house1_channel_5))
    #print(minute_data)
    #combined_frame = combine_dataframes(minute_data, minute_data_2)
    plot_power_usage(minute_data)


main()









