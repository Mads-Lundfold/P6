import pandas as pd
import matplotlib.pyplot as plt
import sys
import datetime

from data_analysis import get_data_from_house, plot_power_usage
from power_thresholds import house2_power_thresholds

#TODO Make paths more general in usage_duration()
#TODO Make code beautiful


dataset = str(sys.argv[1])
house_1 = dataset + "/house_1"
house_2 = dataset + "/house_2"
house_3 = dataset + "/house_3"
house_4 = dataset + "/house_4"
house_5 = dataset + "/house_5"

QUARTERS_IN_DAY = 24*4 #96 quarters in a day


# Shows how much watt each appliance uses at each quater of each day - With thresholds given as a dict
def watt_usage(df: pd.DataFrame, thresholds: dict):

    # Convert unix timestamps to datetime hour:minute:seconds
    df.index = pd.to_datetime(df.index, unit='s').time

    # Groupby time index to get frequencies
    time_grouped_df = df.groupby(df.index).sum()
     
    # Apply thresholds to each appliance
    for appliance, threshold in thresholds.items():
        # Only keep the rows where the appliance usage is greater than the threshold
        time_grouped_df.loc[time_grouped_df[appliance] < threshold, appliance] = 0

    return time_grouped_df

#Plots for each appliance and its typical durations
def usage_duration():
    # Load the CSV file into a Pandas DataFrame, assuming no column names are present
    df = pd.read_csv('C:/Users/VikZu/repos/P6/data_analysis/dataframes/house_2_events.csv', header=None)

    # Rename the columns to something meaningful
    df.columns = ['start_time', 'end_time', 'appliance', 'day']

    # Remove all rows corresponding to "laptop"
    df = df.drop(index=df[df['appliance'] == 'aggregate'].index)

    # Compute the duration of each appliance for each day
    df['duration'] = df['end_time'] - df['start_time']
    duration_by_day = df.groupby(['day', 'appliance'])['duration'].sum().reset_index()

    # Plot a separate graph for each appliance
    for appliance in duration_by_day['appliance'].unique():
        appliance_df = duration_by_day[duration_by_day['appliance'] == appliance]
        pivot_df = appliance_df.pivot(index='day', columns='appliance', values='duration').fillna(0)
        pivot_df.plot(kind='bar', stacked=True)
        plt.title(f'{appliance} Durations by Day')
        plt.xlabel('Day')
        plt.ylabel('Duration (seconds)')
        plt.show()




# Running it
#usage_duration()

watt_df, on_off_df = get_data_from_house(house_number = house_2)
watt_df_removed = watt_df.drop(columns=['aggregate'])
watt_usage_df = watt_usage(watt_df_removed, house2_power_thresholds)
plot_power_usage(watt_usage_df)
print(watt_usage_df)