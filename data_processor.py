import os
import polars as pl
import glob

DATA_DIRECTORY = "./s3_data"

def find_json_files(directory):
    return glob.glob(f"{directory}/**/*.json", recursive=True)

def read_and_concatenate_json_files(directory, column_types):
    json_files = find_json_files(directory)
    df_list = [pl.read_json(file) for file in json_files]
    combined_df = pl.concat(df_list)
    
    # Parse datetime strings to datetime format
    combined_df = combined_df.with_columns(
        pl.col("datetime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M").alias("datetime")
    )
    return combined_df
def convert_to_csv(): 
    column_types = {
        "datetime": pl.Datetime,  # Example: casting 'datetime' column to Datetime type
        "swimmers": pl.Int32,     # Example: casting 'swimmers' column to Int32 type
        "gymmers": pl.Int32,      # Example: casting 'gymmers' column to Int32 type
        "gymmers:": pl.Int32      # Example: casting 'gymmers:' column to Int32 type
    }
    # Read and concatenate JSON files, and cast columns to specified types
    combined_df = read_and_concatenate_json_files(DATA_DIRECTORY, column_types)
    
    print(combined_df)

    # Combine 'gymmers' and 'gymmers:' columns
    combined_df = combined_df.with_columns(
        pl.coalesce([pl.col("gymmers").cast(pl.Int32), pl.col("gymmers:").cast(pl.Int32)]).alias("gymmers")
    )

    print(df)
    
    # df = pl.scan_ndjson('./s3_data/year=2024/*.json')
    
    # print(df)
    

if __name__ == "__main__":
    convert_to_csv()
