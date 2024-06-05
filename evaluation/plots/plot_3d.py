from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from evaluation.dataframe import get_dataframe

range_start = 0
range_end = -1
range_step = 1

# folder = "important_logs/"
# folder = "logs/"
folder = "local_logs/"
files = ["subprocess-2024-04-30-10-52-31.log"]

dfs = []
for file in files:
    path = Path(folder, file)
    print(f"Reading: {path}")
    dfs.append(get_dataframe(path, 'sgx'))
df = pd.concat(dfs)

fig = plt.figure(figsize=plt.figaspect(0.33))

ax = fig.add_subplot(1, 3, 1, projection='3d')
ax.scatter3D(df['Voltages'], df['Widths'], df['Errors'])

ax = fig.add_subplot(1, 3, 2, projection='3d')
ax.scatter3D(df['Voltages'], df['Delays After Trigger'], df['Errors'])

ax = fig.add_subplot(1, 3, 3, projection='3d')
ax.scatter3D(df['Widths'], df['Delays After Trigger'], df['Errors'])

plt.show()
