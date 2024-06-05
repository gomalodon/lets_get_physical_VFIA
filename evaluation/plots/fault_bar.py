from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from evaluation.dataframe import get_dataframe


folder = r"C:\Users\gielo\Documents\School\Burgie_master_2\thesis\data\logs\ANALYZED\sgx_iterations"
files = ["subprocess-2024-05-13-11-04-36_1000_iters.log"]
attack_type = 'sgx'

dfs = []
for file in files:
    path = Path(folder, file)
    print(f"Reading: {path}")
    dfs.append(get_dataframe(path, attack_type))
df = pd.concat(dfs)

x = 'Delays After Trigger'
y = ['Faults', 'Errors', 'Regular Rounds']


sns.set_style("ticks")
df.set_index(x, inplace=True)
ax = df[y].plot(kind='bar', stacked=True, color=['blue', 'red', 'lime'], width=0.8)

# for container in ax.containers:
#     ax.bar_label(container, label_type='center')

plt.xlabel(x)
plt.ylabel('Rounds')
plt.ylim(-30, 1030)
plt.xticks(rotation=0)
plt.legend(loc='upper center', 
           bbox_to_anchor=(0.5, 1.12),
           ncol=3, 
           fancybox=True)

plt.tight_layout()
plt.show()
