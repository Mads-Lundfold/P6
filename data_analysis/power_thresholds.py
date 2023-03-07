import pandas as pd

'''
Dicts for power thresholds.
The dicts should be read as the threshold of the channels in each given house.
If a channel isn't specified, it has a threshold of 5.
'''
house1_power_thresholds = {
    'channel_5' : 20,
    'channel_6' : 10,
    'channel_7' : 10,
    'channel_9' : 20,
    'channel_10' : 2000,
    'channel_11' : 1000,
    'channel_12' : 50,
    'channel_13' : 200,
    'channel_37' : 2,
    'channel_38' : 1,
    'channel_42' : 10
}

house2_power_thresholds = {
    'channel_8' : 2000,
    'channel_12' : 20,
    'channel_13' : 10,
    'channel_14' : 50,
    'channel_15' : 200
}

house3_power_thresholds = {
    'channel_2' : 2000
}

house4_power_thresholds = {
    'channel_3' : 2000,
    'channel_5' : 50,
    'channel_6' : 20
}

house5_power_thresholds = {
    'channel_18' : 2000,
    'channel_19' : 50,
    'channel_22' : 10,
    'channel_23' : 200,
    'channel_24' : 20
}

def apply_power_thresholds(watt_dataframe: pd.DataFrame, house_num: str) -> pd.DataFrame:
    threshold_dict = {}
    threshold_df = pd.DataFrame()

    #Python apparently doesn't have a switch statement lol
    if house_num == 'house_1': threshold_dict = house1_power_thresholds
    if house_num == 'house_2': threshold_dict = house2_power_thresholds
    if house_num == 'house_3': threshold_dict = house3_power_thresholds
    if house_num == 'house_4': threshold_dict = house4_power_thresholds
    if house_num == 'house_5': threshold_dict = house5_power_thresholds
    
    for column in watt_dataframe:
        threshold_df[column] = watt_dataframe[column].apply(lambda power: power if (power > threshold_dict.get(column, 5)) else 0)
    
    return threshold_df


