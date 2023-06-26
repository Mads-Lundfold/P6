import pandas as pd

house_1_removable_appliances = ['aggregate', 'boiler', 'solar_thermal_pump', 'fridge', 'adsl_router', 'lighting_circuit', 'data_logger_pc', 'livingroom_s_lamp','soldering_iron','gigE_&_USBhub','kitchen_dt_lamp', 'bedroom_ds_lamp', 'livingroom_s_lamp2', 'iPad_charger', 'livingroom_lamp_tv', 'kitchen_lamp2', 'utilityrm_lamp','samsung_charger', 'bedroom_d_lamp', 'bedroom_chargers', 'childs_table_lamp','childs_ds_lamp','battery_charger','office_lamp1', 'office_lamp2','office_lamp3','LED_printer','kitchen_lights']

def remove_appliances(house_df: pd.DataFrame):
    return house_df.drop(columns=house_1_removable_appliances)