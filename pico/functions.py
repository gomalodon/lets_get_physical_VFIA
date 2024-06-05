import time
import _thread
from machine import Pin, I2C

FREQ = 1_000_000
VR_ADDR = 0x5e
I2C_INTERFACE = I2C(0, scl=Pin("GP17"), sda=Pin("GP16"), freq=FREQ)
# I2C_INTERCEPT = Pin("GP17", Pin.OUT)
# I2C_INTERCEPT.value(0)

TRIGGER_PIN = Pin("GP15", Pin.OUT)
LED_PIN = Pin("LED", Pin.OUT)
STARTUP_PIN = Pin("GP14", Pin.OUT)
STARTUP_PIN.value(1)


global continuous_voltage, writing
continuous_voltage: str = None
writing = False


def scan():
    devices = I2C_INTERFACE.scan()
    if devices:
        for d in devices:
            print(hex(d))
    else:
        print("None found")
    return devices


def mfr_vboot():
    I2C_INTERFACE.writeto(VR_ADDR, b"\xe5")
    print("MFR_VBOOT_SET: ")
    print(I2C_INTERFACE.readfrom(VR_ADDR, 8))


def write_voltage(voltage: str, trig: bool = False, continuous: str = None) -> None:
    global continuous_voltage, writing
    writing = True
    if trig:
        trigger()
    temp = continuous_voltage  # stop sending continuous packets, but afterwards restart it
    continuous_voltage = None
    # I2C_INTERCEPT.value(1)  # Allow temporary write
    I2C_INTERFACE.writeto(VR_ADDR, bytes.fromhex("21" + voltage[2:]))
    if temp:  # return as quickly as possible to a higher value
        I2C_INTERFACE.writeto(VR_ADDR, bytes.fromhex("21" + temp[2:]))
    # I2C_INTERCEPT.value(0)
    continuous_voltage = continuous if continuous else temp
    writing = False


def blink(n: int) -> None:
    while n > 0:
        LED_PIN.on()
        time.sleep(1)
        LED_PIN.off()
        time.sleep(1)
        n -= 1


def led_on() -> None:
    LED_PIN.on()


def led_off() -> None:
    LED_PIN.off()


def trigger() -> None:
    TRIGGER_PIN.value(1)
    time.sleep(0.002)
    TRIGGER_PIN.value(0)


def loop_up() -> None:
    # base = 1.0
    base = 0.778
    trigger()
    for i in range(1000):
        print(i / 1000)
        write_voltage(base + i / 1000)
        time.sleep(0.001)


def loop_down() -> None:
    # base = 1.0
    base = 0.778
    trigger()
    for i in range(777):
        print(i / 1000)
        write_voltage(base - i / 1000)
        time.sleep(0.001)


def on_off(timeout: float = 2.0) -> None:
    set_global_voltage(None)
    STARTUP_PIN.value(0)
    time.sleep(timeout)
    STARTUP_PIN.value(1)


def restart(startup_time: float = 31.0, delay1: float = 11.0, delay2: float = 2.0, timeout: float = 2.0) -> None:
    set_global_voltage(None)
    on_off(delay1)
    time.sleep(timeout)
    on_off(delay2)
    time.sleep(startup_time)


def set_global_voltage(voltage: str = None):
    global continuous_voltage
    continuous_voltage = voltage


# b'handled exception in thread started by <function
# continuous_voltage at 0x20016520>\r\nTraceback (most recent call
# last):\r\n  File "functions.py", line 122, in continuous_voltage\r\n
# File "functions.py", line 46, in write_voltage\r\nOSError: [Errno 5]
# EIO\r\nR\x01\x80\x00\x01'
def continuous_voltage() -> None:
    global continuous_voltage, writing
    continuous_voltage = None
    while True:
        if not writing and continuous_voltage:
            try:
                write_voltage(continuous_voltage)
            except OSError:
                pass



def fastest_write(v1: str = "0x10", v2: str = "0x20"):
    trigger()
    I2C_INTERFACE.writeto(VR_ADDR, bytes.fromhex("21" + v1[2:]))
    I2C_INTERFACE.writeto(VR_ADDR, bytes.fromhex("21" + v2[2:]))


_thread.start_new_thread(continuous_voltage, ())
led_on()
