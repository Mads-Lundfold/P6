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

    # Remove all rows corresponding to "laptop"
    df = df.drop(columns='aggregate')

    # Groupby time index to get frequencies
    frequencies = df.groupby(df.index).sum()

    return frequencies


# Make a chart for the usage frequency of each appliance.
def plot_frequencies(df: pd.DataFrame):
    for appliance in df.columns:
        df[appliance].plot(title=appliance, kind='area')
        plt.show()


def get_time_associations(df: pd.DataFrame, events_csv: __file__, threshold: float):
    
    # Count how many event of each appliance there is in the event csv
    event_df = pd.read_csv(events_csv, header=None, names=['start', 'end', 'appliance', 'value'])
    appliance_occurence_dict = event_df['appliance'].value_counts().to_dict()

    # Find out how many total usages the appliance has in total
    '''# Divide each entry of an appliance in df by its corresponding total_occurence
    for appliance in df.columns:
        total_occurence = appliance_occurence_dict.get(appliance, 1) # set default to 1 if appliance not found
        df[appliance] = df[appliance] / total_occurence * 100
        df[appliance] = df[appliance].round(2) # round to 2 decimal places'''
    
    # Find the maximum value of each appliance in df and store in a dictionary
    max_values_dict = {appliance: df[appliance].max() for appliance in df.columns}

    for appliance in df.columns:
        max_occurence = max_values_dict.get(appliance, 1) # set default to 1 if appliance not found
        df[appliance] = df[appliance] / max_occurence * 100
        df[appliance] = df[appliance].round(2) # round to 2 decimal places
    
    # Replace values less than threshold with 0 in df
    #df = df.where(df >= threshold, other=0)

    # Get time for which there is some non-zero value in df
    '''time_intervals_where_app_can_be_used = {}
    for appliance in df.columns:
        intervals = []
        for time in df.index:
            #Only take time intervals where the entry is bigger or equals the threshold
            if df[appliance][time] >= threshold:
                intervals.append(time)
        time_intervals_where_app_can_be_used[appliance] = intervals'''
    
    # Get time intervals (start, end) for which there is some non-zero value in df
    time_intervals_where_app_cannot_be_used = {}
    for appliance in df.columns:
        intervals = []
        start_time = None
        for time in df.index:
            if df[appliance][time] <= threshold and start_time is None:
                start_time = time
            elif df[appliance][time] > threshold and start_time is not None:
                end_time = time
                intervals.append((start_time, end_time))
                start_time = None
        if start_time is not None:
            end_time = df.index[-1]
            intervals.append((start_time, end_time))
        time_intervals_where_app_cannot_be_used[appliance] = intervals

    print(time_intervals_where_app_cannot_be_used)
    return df, time_intervals_where_app_cannot_be_used

# Running it
def get_restricted_times():
    watt_df, on_off_df = get_data_from_house(house_number = house_3) 
    frequencies = usage_frequencies(on_off_df)
    time_associations_start_finish, unusable_time_intervals_all_appliances = get_time_associations(frequencies, './dataframes/house_3_events.csv', 30)
    return unusable_time_intervals_all_appliances