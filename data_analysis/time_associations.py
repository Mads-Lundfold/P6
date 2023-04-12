import pandas as pd
import matplotlib.pyplot as plt
import sys
import datetime

from data_analysis import get_data_from_house


#TODO Improve paths to house data, so it doesn't have to be called from this file.
#TODO Ensure that the on/off dataframes begin at midnight so frequencies aren't scewed.
#TODO Add Niklas' helper functions to ensure correctness.


dataset = str(sys.argv[1])
house_1 = dataset + "/house_1"
house_2 = dataset + "/house_2"
house_3 = dataset + "/house_3"
house_4 = dataset + "/house_4"
house_5 = dataset + "/house_5"

QUARTERS_IN_DAY = 24*4 #96 quarters in a day


# Counts how often each appliance is used at each quater of each day
def usage_frequencies(df: pd.DataFrame):

    # Convert values in dataframe from boolean to int (0,1)
    df = df.astype(int)

    # Convert unix timestamps to datetime hour:minute:seconds
    df.index = pd.to_datetime(df.index, unit='s').time

    # Groupby time index to get frequencies
    frequencies = df.groupby(df.index).sum()

    return frequencies


# Make a chart for the usage frequency of each appliance.
def plot_frequencies(df: pd.DataFrame):
    for appliance in df.columns:
        df[appliance].plot(title=appliance, kind='area')
        plt.show()



# Running it
watt_df, on_off_df = get_data_from_house(house_number = house_3) 
frequencies = usage_frequencies(on_off_df)
print(frequencies)
plot_frequencies(frequencies)