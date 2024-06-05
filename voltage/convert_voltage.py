import struct


def reverse(v):
    a = v * 8192.0
    b = int(a) << 32
    return b

def actual_voltage(msr_response):
    a = (msr_response & 0xFFFF00000000) >> 32
    return a / 8192.0

v = 0x1eb800001400
print(actual_voltage(v))

v = 1.2
print(hex(reverse(v)))

# v = 0x1f5c00001400
# print(actual_voltage(v))
# v = 0x00140000E11E
# print(actual_voltage(v))

0x266600001400