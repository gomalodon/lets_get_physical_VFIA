import seaborn as sns
from datetime import datetime
import pandas as pd
import os
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

FILENAME = ["data/data-", 0, ".txt"]
WRITE_FILE = False
PRINT_DATA = False
SHOWN_VALUES = 30
DELAY = 500


def get_filename():
    fn = "".join(str(s) for s in FILENAME)
    if os.path.exists(fn):
        FILENAME[1] += 1
        fn = get_filename()
    return fn


def write_file(location, data, write_type='a'):
    with open(location, write_type) as f:
        f.write(data)


def actual_voltage(msr_response):
    a = (msr_response & 0xFFFF00000000) >> 32
    return a / 8192.0


def get_voltage(fd):
    msr_198 = struct.unpack("<Q", os.pread(fd, 8, 0x198))[0]
    return actual_voltage(msr_198)


def update(frame):
    voltage = get_voltage(fd)
    time = datetime.now()
    if WRITE_FILE:
        write_file(filename, f"{time}|{voltage}\n")
    if PRINT_DATA:
        print(f"{time}   -   {voltage:.5f}V")

    df.loc[len(df)] = [time, voltage]

    ax.relim()
    ax.autoscale_view()
    line.set_data(df['Timestamp'][-SHOWN_VALUES:-1], df['Voltage'][-SHOWN_VALUES:-1])
    return line,


if os.geteuid() != 0:
    exit("Need root privileges.")
try:
    fd = os.open("/dev/cpu/0/msr", os.O_RDWR)
except OSError:
    exit("Could not open /dev/cpu/0/msr")
filename = get_filename()

df = pd.DataFrame(columns=['Timestamp', 'Voltage'])
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot_date([], [], linestyle='solid')
# ax.set_ylim([0, 2])
ax.set_xlabel('Timestamp')
ax.set_ylabel('Voltage')
ax.tick_params(rotation=60)

animation = FuncAnimation(fig, update, frames=None, interval=DELAY, save_count=0)
plt.tight_layout()
plt.show()
