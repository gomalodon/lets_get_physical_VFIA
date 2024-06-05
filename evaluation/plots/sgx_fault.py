import math
import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from evaluation.dataframe import get_dataframe


folder = r"C:\Users\gielo\Documents\School\Burgie_master_2\thesis\data\logs\ANALYZED\sgx_iterations"
files = os.listdir(folder)
# files = ["test-subprocess-2024-05-11-13-04-49.log"]   
attack_type = 'sgx'


dfs = []
for file in files:
    path = Path(folder, file)
    print(f"Reading: {path}")
    dfs.append(get_dataframe(path, attack_type))
df = pd.concat(dfs)

all_y_axis = {
    'Ratios': '(ones to zeros)',
    'Lenstra': '',
    'Bellcore': '',
}
df = df[list(all_y_axis.keys())]
df = df[df['Ratios'].notna()]
# print(df.columns)
# print(df)

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(math.ceil(len(all_y_axis.keys()) / 2), 2)

for i, v in enumerate(all_y_axis.items()):
    y_axis, key = v
    a = axes[i // 2, i % 2]
    sns.scatterplot(ax=a, x=df.index.values, y=y_axis, data=df, marker='o', s=10, linewidth=0)
    # a.set_title(y_axis)
    # a.set_xlabel(x_axis)
    a.set_ylabel(f"{y_axis} {key}")
    a.tick_params(axis='x', rotation=60)
i += 1
r, c = fig.axes[0].get_subplotspec().get_gridspec().get_geometry()
while i < r * c:
    fig.delaxes(axes[i // 2, i % 2])
    i += 1


print('\n\n\nRESULTS:\n')
print(f"Ratios: mean = {df['Ratios'].mean()}, stdev = {df['Ratios'].std()}")
print()
print(df['Lenstra'].value_counts())
print()
print(df['Bellcore'].value_counts())

print()

plt.tight_layout()
plt.show()
