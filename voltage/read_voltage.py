import curses
import os
import struct
from datetime import datetime

# ONLY WORKS ON UNIX
# conversion from https://github.com/KitMurdock/plundervolt/blob/master/utils/read_voltage.c
# run: sudo python3 read_voltage.py

DELAY = 500
FILENAME = ["data-", 0, ".txt"]


def get_filename():
    filename = "".join(str(s) for s in FILENAME)
    if os.path.exists(filename):
        FILENAME[1] += 1
        filename = get_filename()
    return filename


def write_file(location, data, write_type='a'):
    with open(location, write_type) as f:
        f.write(data)


def actual_voltage(msr_response):
    a = (msr_response & 0xFFFF00000000) >> 32
    return a / 8192.0


def get_voltage(fd):
    msr_198 = struct.unpack("<Q", os.pread(fd, 8, 0x198))[0]
    return actual_voltage(msr_198)


def main(stdscr):
    if os.geteuid() != 0:
        exit("Need root privileges.")

    # check if we can open the msr
    try:
        fd = os.open("/dev/cpu/0/msr", os.O_RDWR)
    except OSError:
        stdscr.addstr(0, 0, "Could not open /dev/cpu/0/msr")
        stdscr.refresh()
        stdscr.getch()
        return

    curses.curs_set(0)

    filename = get_filename()

    while True:
        voltage = get_voltage(fd)
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        write_file(filename, f"{time}|{voltage}\n")

        stdscr.clear()
        stdscr.addstr(0, 0, f"Time: {time}\nVoltage: {voltage:.5f} V")
        stdscr.refresh()

        curses.napms(DELAY)


if __name__ == "__main__":
    curses.wrapper(main)
