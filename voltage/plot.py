import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import seaborn as sns

with open("data.txt", "r") as f:
    data = f.read().split('\n')

# Parse data
timestamps = []
voltages = []
for entry in data:
    try:
        timestamp_str, voltage_str = entry.split('|')
    except ValueError:
        continue
    timestamps.append(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"))
    voltages.append(float(voltage_str))

df = pd.DataFrame({'Timestamp': timestamps, 'Voltage': voltages})

sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.lineplot(x='Timestamp', y='Voltage', data=df, marker='o', estimator=None)
plt.title('Data')
plt.xlabel('Timestamp')
plt.ylabel('Voltage')
plt.xticks(rotation=60)
plt.tight_layout()
plt.show()
