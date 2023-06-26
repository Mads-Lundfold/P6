# Generate watt dataframe for house one. Delimited within 2014. Missing a list of uninterresting appliances.

import sys
import os
import pandas as pd
import datetime
from pathlib import Path
from appliance_removal import remove_appliances
from data_analysis import get_data_from_house, write_dataframe_to_csv

dataset = str(sys.argv[1])
house_1 = dataset + "/house_1"

# Feb 27 2013 20:30:00 -> 1361997000
# Apr 08 2013 05:00:00 -> 1365397200
# looking to delimit just march

MARCH_BEGIN = 1362092400
APRIL_BEGIN = 1364767200

YEAR_2014_GMT_BEGIN = 1388534400
YEAR_2015_GMT_BEGIN = 1420070400


def write_dataframe_to_csv_headers(dataframe : pd.DataFrame, filename : str) -> None: 
    filepath = Path(f'dataframes/{filename}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    dataframe.to_csv(filepath, index=True, index_label='Time', header=True)


def generate_2014_h1_thin()-> None:
    watt_df, on_off_df = get_data_from_house(house_1)
    watt_df = watt_df[(watt_df.index >= YEAR_2014_GMT_BEGIN) & (watt_df.index <= YEAR_2015_GMT_BEGIN)]
    on_off_df = on_off_df[(on_off_df.index >= YEAR_2014_GMT_BEGIN) & (on_off_df.index <= YEAR_2015_GMT_BEGIN)]
    print(watt_df)
    print(on_off_df)
    watt_df = remove_appliances(watt_df)
    print(watt_df)
    on_off_df = remove_appliances(on_off_df)
    print(on_off_df)
    #write_dataframe_to_csv_headers(watt_df, 'house_1_2014_15min_watts')
    write_dataframe_to_csv_headers(on_off_df, 'house_1_2014_15min_on_off_NEW')

    return

def load_lvl_1_df()-> None:
    start = datetime.datetime.now()
    df = pd.read_csv('./dataframes/house_1_2014_15min_watts.csv')
    end = datetime.datetime.now()
    difference = end-start
    print(difference)


generate_2014_h1_thin()