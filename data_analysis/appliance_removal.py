import pandas as pd

house_1_removable_appliances = ['aggregate', 'boiler', 'solar_thermal_pump', 'fridge', 'adsl_router', 'ligting_circuit', 'data_logger_pc']

def remove_appliances(house_df: pd.DataFrame):
    return house_df.drop(columns=house_1_removable_appliances)