import pandas as pd

import matplotlib.pyplot as plt

df = pd.read_csv('./output/DTSC.csv')

print(df.dtypes)

df['datetime'] = pd.to_datetime(df['datetime'])
df['datetime'] = df['datetime'].dt.tz_localize('UTC')
df['datetime'] = df['datetime'].dt.tz_convert('Asia/Taipei')

plt.figure(figsize=(20, 6))

# Plot swimmers
plt.scatter(df['datetime'], df['swimmers'], color='blue', label='Swimmers', alpha=0.6)

# Plot gymmers
# plt.scatter(df['datetime'], df['gymmers'], color='green', label='Gymmets', alpha=0.6)

# Format the plot
plt.title('Counts of Swimmers and Gymmers Over Time')
plt.xlabel('Datetime')
plt.ylabel('Count')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.show()
