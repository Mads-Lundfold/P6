import pandas as pd
import matplotlib.pyplot as plt
import sys

from data_analysis import get_data_from_house


#TODO Improve paths to house data, so it doesn't have to be called from this file.
#TODO Ensure that the on/off dataframes begin at midnight so frequencies aren't scewed
#TODO Add Niklas' helper functions to ensure correctness


dataset = str(sys.argv[1])
house_1 = dataset + "/house_1"
house_2 = dataset + "/house_2"
house_3 = dataset + "/house_3"
house_4 = dataset + "/house_4"
house_5 = dataset + "/house_5"

QUARTERS_IN_DAY = 24*4 #96 quarters in a day


# Counts how often each appliance is used at each quater of each day
def usage_frequencies(on_off_df: pd.DataFrame):

    # Convert bool values to int (0,1)
    on_off_df = on_off_df.astype(int)

    # Split full dataframe into list of daily dataframes
    chunk_list = chunkify(on_off_df, chunk_size=QUARTERS_IN_DAY*900)

    # Add each daily dataframe together to get how often the appliances were used at each quater of the day
    freq = chunk_list[0]

    for i in range(1, len(chunk_list)):
        freq = freq.add(chunk_list[i], fill_value=0)

    return freq


# Slices bigger dataframes into daily dataframes
def chunkify(df: pd.DataFrame, chunk_size: int):

    # Slice dataframe into daily dataframes
    chunk_list = [df.loc[i : i+chunk_size] for i in range(df.index[0], df.index[-1], chunk_size)]
    
    # Change 'time' column for each chunk from the unix timestamp to the time of the given day.
    # The first time (00:00) should be 0, whereas the last time (23:45) should be 86400, as that's the amount of seconds from the start.
    for chunk in chunk_list:
        if len(chunk) > 0:
            start = chunk.index[0]
        
            for i in range(0, len(chunk)):
                chunk.rename(index={chunk.index[i] : (chunk.index[i] - start)}, inplace=True)

    return chunk_list


# Make a chart for the usage frequency of each appliance.
def plot_frequencies(df: pd.DataFrame):
    for appliance in df.columns:
        df[appliance].plot(title=appliance, kind='area')
        plt.show()



# Running it
watt_df, on_off_df = get_data_from_house(house_number = house_3) 
frequencies = usage_frequencies(on_off_df=on_off_df)
plot_frequencies(frequencies)