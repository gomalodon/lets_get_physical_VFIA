import os
import struct

"""

Not possible, will give OSError

"""


def reverse_conversion(v):
    return int(v * 8192.0) << 32

def actual_voltage(msr_response):
    a = (msr_response & 0xFFFF00000000) >> 32
    return a / 8192.0

def write_voltage(fd, v):
    msr_v = struct.pack("<Q", reverse_conversion(v))
    print("writing:")
    print(msr_v)
    os.pwrite(fd, msr_v, 0x198)

def get_voltage(fd):
    msr_198 = struct.unpack("<Q", os.pread(fd, 8, 0x198))[0]
    return actual_voltage(msr_198)


if __name__=="__main__":
    if os.geteuid() != 0:
        exit("Need root privileges.")

    try:
        fd = os.open("/dev/cpu/0/msr", os.O_RDWR)
    except OSError:
        print("could not open msr")
        exit(-1)

    write_voltage(fd, 1.2)