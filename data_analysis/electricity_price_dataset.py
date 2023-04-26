import pandas as pd

def read_extract_convert_price_dataset():

    # Read the CSV file into a DataFrame
    df = pd.read_csv("data\Electricity_price_dataset_new.csv", header=None, names=["utc_timestamp", "cet_cest_timestamp", "GB_GBN_price_day_ahead"], delimiter=",", skiprows=[1])
    
    # Extract only col1 and col3 columns
    df = df[["utc_timestamp", "GB_GBN_price_day_ahead"]]

    # Convert col1 from ISO 8601 to Unix timestamp
    timestamps = []
    for timestamp_str in df["utc_timestamp"]:
        try:
            timestamp = pd.to_datetime(timestamp_str)
            timestamp_unix = int(timestamp.timestamp())
            timestamps.append(timestamp_unix)
        except ValueError:
            timestamps.append(None)
    df["utc_timestamp"] = timestamps

    # Remove rows with missing timestamps
    df.dropna(inplace=True)

    # Rename the first column to "unix_timestamp"
    df = df.rename(columns={"utc_timestamp": "unix_timestamp"})

    # Convert GB_GBN_price_day_ahead from string to float, then to integer and then into WH from MWh
    df["GB_GBN_price_day_ahead"] = df["GB_GBN_price_day_ahead"].astype(float).astype(int) / 1000000

    return df


def main():
    price_df = read_extract_convert_price_dataset()
    print(price_df)

main()