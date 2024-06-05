from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

folder = r"C:\Users\gielo\Documents\School\Burgie_master_2\thesis\data"
file = "freq-volt.csv"

df = pd.read_csv(Path(folder, file))
# print(df.columns)


d = {
    'Set Frequency': '(GHz)',
    'Actual Frequency': '(GHz)', 
    'Core Voltage': '(V)',
    'Spikes': ''
}

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 2)

def line(a, x_axis, y_axis):
    sns.lineplot(data=df, ax=a, x=x_axis, y=y_axis)
    a.set_xlabel(f"{x_axis} {d[x_axis]}")
    a.set_ylabel(f"{y_axis} {d[y_axis]}")


line(axes[0, 0], 'Set Frequency', 'Actual Frequency')
line(axes[0, 1], 'Actual Frequency', 'Core Voltage')
line(axes[1, 0], 'Actual Frequency', 'Spikes')
fig.delaxes(axes[1, 1])

plt.tight_layout()
plt.show()