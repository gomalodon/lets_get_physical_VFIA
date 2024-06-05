import math
import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from evaluation.dataframe import get_dataframe


"""
    'Timestamp'
    'Errors'
    'Crashes'
    'Faults'
    'Rounds'
    'Iterations'
    'Voltages'
    'Widths'
    'Delays After Trigger'
"""

folder = r"C:\Users\gielo\Documents\School\Burgie_master_2\thesis\data\logs\ANALYZED\sgx_iterations"
# files = ["subprocess-2024-05-12-19-24-14-one-iteration.log", "test-subprocess-2024-05-11-13-04-49.log"]
files = os.listdir(folder)
attack_type = 'sgx'


dfs = []
for file in files:
    path = Path(folder, file)
    print(f"Reading: {path}")
    dfs.append(get_dataframe(path, attack_type))
df = pd.concat(dfs)

# df.to_csv('test.csv')

x_axis = 'Timestamp'
all_y_axis = {
    'Errors': '',
    'Crashes': '',
    'Faults': '',
    'Iterations': '',
    'Voltages': '(V)',
    'Widths': '(us)',
    'Delays After Trigger': '(us)'
}

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(math.ceil(len(all_y_axis.keys()) / 2), 2, figsize=(16, 8))

for i, v in enumerate(all_y_axis.items()):
    y_axis, key = v
    a = axes[i // 2, i % 2]
    sns.scatterplot(ax=a,
                    x=x_axis,
                    y=y_axis,
                    data=df,
                    marker='o',
                    s=10,
                    linewidth=0)
    # a.set_title(y_axis)
    # a.set_xlabel(x_axis)
    a.set_ylabel(f"{y_axis} {key}")
    a.tick_params(axis='x', rotation=60)

i += 1
r, c = fig.axes[0].get_subplotspec().get_gridspec().get_geometry()
while i < r * c:
    fig.delaxes(axes[i // 2, i % 2])
    i += 1

plt.tight_layout()
plt.show()
