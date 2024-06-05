import math
import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from evaluation.dataframe import get_dataframe

# folder = r"C:\Users\gielo\Documents\School\Burgie_master_2\thesis\data\logs\ANALYZED\sgx_iterations"
folder = r"C:\Users\gielo\Documents\School\Burgie_master_2\thesis\data\logs"
# files = ["subprocess-2024-05-11-13-04-49.log"] # 100 iterations
# files = ["subprocess-2024-05-12-19-24-14-one-iteration.log"]  # 1 iterations 1000
# files = ["subprocess-2024-05-12-19-24-14-one-iteration.log",
        #  "subprocess-2024-05-19-20-55-45.log"]  # good error histogram
# files = [r"one_iteration\subprocess-2024-05-19-20-55-45.log"]
files = [r"1-test\subprocess-2024-05-27-15-01-06.log"]
# files = os.listdir(folder)
attack_type = 'sgx'

x = 'Delays After Trigger'
y = ['Faults', 'Errors', 'Regular Rounds']
x_lims = None
# x_lims = (700000, 830000)
tick_gap = 25

plot_in_white = False
plot_simple = False
plot_bar = True
print_stats = True


dfs = []
for file in files:
    path = Path(folder, file)
    print(f"Reading: {path}")
    dfs.append(get_dataframe(path, attack_type)[[x, *y]])
df = pd.concat(dfs)

df = df.groupby(x).mean().reset_index()
df = df.sort_values(by=x)


if x_lims is not None:
    df = df[df[x].between(x_lims[0], x_lims[1])]

print(df)
# df.to_csv('test.csv')

if print_stats:
    for i in y:
        print(f"{i} mean: {df[i].mean()}, stdev: {df[i].std()}, median: {df[i].median()}, max: {df[i].max()}, min: {df[i].min()}")

if plot_simple:
    sns.set_theme(style="whitegrid")
    fig = plt.figure()
    for i in y[:-1]:
        sns.scatterplot(x=x, y=i, data=df, marker='o', s=10, linewidth=0)
    fig.legend(y[:-1], loc='upper center',
               ncol=2,
               fancybox=True)

if plot_bar:
    colors = ['blue', 'red', 'lime']
    if plot_in_white:
        colors = colors[:-1]
        y = y[:-1]
    sns.set_style("ticks")
    df.set_index(x, inplace=True)
    ax = df[y].plot(kind='bar', stacked=True, color=colors, width=1.0, edgecolor="none", figsize=(16, 12))

    # for container in ax.containers:
    #     ax.bar_label(container, label_type='center')
    plt.xlabel(x)
    plt.ylabel('Rounds')
    # plt.ylim(0, 1)
    plt.xticks(rotation=45)
    plt.legend(loc='upper center',
               bbox_to_anchor=(0.5, 1.05),
               ncol=3,
               fancybox=True)

    xticks = ax.xaxis.get_major_ticks()
    for i in range(len(xticks)):
        if i % tick_gap == 0:
            xticks[i].set_visible(True)
        else:
            xticks[i].set_visible(False)

plt.tight_layout()
plt.show()
