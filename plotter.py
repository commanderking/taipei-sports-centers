import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

SPORTS_CENTER = "ZSSC"

df = pd.read_csv(f'./output/{SPORTS_CENTER}.csv')

df['datetime'] = pd.to_datetime(df['datetime'])
df['datetime'] = df['datetime'].dt.tz_localize('UTC')
df['datetime'] = df['datetime'].dt.tz_convert('Asia/Taipei')

df = df.sort_values("datetime")

# Extract dates and add NaN values for midnight
# This is needed to prevent connecting lines between days
unique_dates = df['datetime'].dt.date.unique()
midnights = [pd.Timestamp(date).tz_localize('Asia/Taipei') for date in unique_dates]
midnight_df = pd.DataFrame({
    'datetime': midnights,
    'swimmers': [np.nan] * len(midnights),
    'gymmers': [np.nan] * len(midnights)
})
df = pd.concat([df, midnight_df]).sort_values('datetime').reset_index(drop=True)


# Plotting a single sports center 
plt.figure(figsize=(20, 6))

plt.plot(df['datetime'], df['swimmers'], color='blue', label='Swimmers', marker='o', markersize=4, alpha=0.6)
plt.plot(df['datetime'], df['gymmers'], color='green', label='Gymmers', alpha=0.6, marker='o', markersize=4)

plt.title(f'Swimmers and Gymmers at {SPORTS_CENTER}')
plt.xlabel('Datetime')
plt.ylabel('Count')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.show()


def average_plot(file_list):
    num_files = len(file_list)
    fig, axs = plt.subplots(num_files, 1, figsize=(12, 2 * num_files), sharex=True, sharey=True)

    for i, file in enumerate(file_list):
        # Load the data
        df = pd.read_csv(file)

        # Localize to Taipei 
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['datetime'] = df['datetime'].dt.tz_localize('UTC')
        df['datetime'] = df['datetime'].dt.tz_convert('Asia/Taipei')

        # Filter the data to include only times between 6 am and 10 pm
        df = df.set_index('datetime')
        df = df.between_time('06:00', '22:00')
        df['time'] = df.index.time

        # Create a time range for every 15 minutes from 6:00 to 22:00
        time_range = pd.date_range('06:00', '22:00', freq='15min').time

        average_swimmers = []
        average_gymmers = []

        # Calculate the mean for each 15-minute period
        for time in time_range:
            period_data = df[df['time'] == time]
            average_swimmers.append(period_data['swimmers'].mean())
            average_gymmers.append(period_data['gymmers'].mean())

        # Create a result DataFrame
        result_df = pd.DataFrame({'time': time_range, 'average_swimmers': average_swimmers, 'average_gymmers': average_gymmers})

        # Convert the 'time' column to string format for plotting
        result_df['time'] = result_df['time'].astype(str)

        # Select the appropriate subplot axis
        ax = axs[i] if num_files > 1 else axs

        # Plot and format
        ax.plot(result_df['time'], result_df['average_swimmers'], color='blue', label='Average Swimmers', marker='o', markersize=4, linestyle='-', alpha=0.6)
        ax.plot(result_df['time'], result_df['average_gymmers'], color='green', label='Average Gymmers', marker='o', markersize=4, linestyle='-', alpha=0.6)
        ax.set_title(f'Average Counts of Swimmers and Gymmers Over Time ({file})')
        ax.set_ylabel('Average Count')
        ax.legend()
        ax.grid(True)

        # Minimize labels shown
        ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
        plt.setp(ax.get_xticklabels(), rotation=45)

    plt.xlabel('Time of Day')
    plt.tight_layout()
    plt.show()

# List of CSV files to read
sports_center_list = ['DTSC', 'JJSC', 'ZSSC', 'WSSC']
csv_paths = []
for center in sports_center_list:
    csv_paths.append(f'./output/{center}.csv')


# Call the averagePlot function with the list of files
average_plot(csv_paths)