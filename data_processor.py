import os
import polars as pl
import glob

DATA_DIRECTORY = "./s3_data"
def find_json_files(directory):
    return glob.glob(f"{directory}/**/*.json", recursive=True)

def read_and_concatenate_json_files(directory):
    json_files = find_json_files(directory)
    df_list = [pl.read_json(file) for file in json_files]
    combined_df = pl.concat(df_list)
    
    # Parse datetime strings to datetime format
    combined_df = combined_df.with_columns(
        pl.col("datetime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M").alias("datetime")
    )
    return combined_df
def convert_to_csv(): 
    # Read and concatenate JSON files, and cast columns to specified types
    combined_df = read_and_concatenate_json_files(DATA_DIRECTORY)
    combined_df.write_csv("./output/combined_data.csv")
    
    unique_centers = combined_df['center'].unique()
    
    for center in unique_centers:
        df = combined_df.filter(pl.col("center") == center)
        df.write_csv(f'./output/{center}.csv')    

if __name__ == "__main__":
    convert_to_csv()
