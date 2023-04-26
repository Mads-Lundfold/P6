import pandas as pd

'''
Dicts for power thresholds.
The dicts should be read as the threshold of the channels in each given house.
If a channel isn't specified, it has a threshold of 5.
'''
house1_power_thresholds = {
    'washing_machine' : 20,
    'dishwasher' : 10,
    'tv' : 10,
    'htpc' : 20,
    'kettle' : 2000,
    'toaster' : 1000,
    'fridge' : 50,
    'microwave' : 200,
    'kitchen_radio' : 2,
    'bedroom_chargers' : 1,
    'gas_oven' : 10
}

house2_power_thresholds = {
    'kettle' : 2000,
    'washing_machine' : 20,
    'dish_washer' : 10,
    'fridge' : 50,
    'microwave' : 200
}

house3_power_thresholds = {
    'kettle' : 2000
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


