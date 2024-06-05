import logging
import argparse
import os
import pathlib
import subprocess
from typing import List, Tuple

import numpy


def voltage_to_hex(voltage: float) -> str:
    assert voltage >= 0.49
    return '{:02x}'.format(int(voltage * 1000 / 10 - 49))


def hex_to_voltage(hex: str) -> float:
    return (int(hex, 16) + 49) * 10 / 1000


class InvalidArgumentException(Exception):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(*args)
        self.message = message

    def __str__(self) -> str:
        return super().__str__() + self.message


def frange(start, stop, step, n=None):
    """
    THX @https://stackoverflow.com/users/1089161/smichr

    return a WYSIWYG series of float values that mimic range behavior
    by excluding the end point and not printing extraneous digits beyond
    the precision of the input numbers (controlled by n and automatically
    detected based on the string representation of the numbers passed).

    EXAMPLES
    ========

    non-WYSIWYS simple list-comprehension

    >>> [.11 + i*.1 for i in range(3)]
    [0.11, 0.21000000000000002, 0.31]

    WYSIWYG result for increasing sequence

    >>> list(frange(0.11, .33, .1))
    [0.11, 0.21, 0.31]

    and decreasing sequences

    >>> list(frange(.345, .1, -.1))
    [0.345, 0.245, 0.145]

    To hit the end point for a sequence that is divisibe by
    the step size, make the end point a little bigger by
    adding half the step size:

    >>> dx = .2
    >>> list(frange(0, 1 + dx/2, dx))
    [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

    """
    if step == 0:
        raise ValueError('step must not be 0')
    # how many decimal places are showing?
    if n is None:
        n = max([0 if '.' not in str(i) else len(str(i).split('.')[1])
                for i in (start, stop, step)])
    if step * (stop - start) > 0:  # a non-null incr/decr range
        if step < 0:
            for i in frange(-start, -stop, -step, n):
                yield -i
        else:
            steps = round((stop - start) / step)
            while round(step * steps + start, n) < stop:
                steps += 1
            for i in range(steps):
                yield round(start + i * step, n)


def convert_args(s: str) -> List[float]:
    s_split = s.split(':')
    if len(s_split) == 1:
        s_split = s_split[0].split(',')
        if len(s_split) == 1:
            return [float(s_split[0])]
        return [float(i) for i in s_split]
    elif len(s_split) == 3:
        v1 = float(s_split[0])
        v2 = float(s_split[1])
        step = float(s_split[2])
        if step < 0:
            return list(frange(max(v1, v2), min(v1, v2) + step / 2, step))
        return list(frange(min(v1, v2), max(v1, v2) + step / 2, step))
    raise InvalidArgumentException(f"range notation was invalid: {s}")


notation_text = """
For certain variables the possible notations are:
    single value    f1                  E.g. 0.5            ->      [0.5]
    list            f1,f2,...           E.g. 0.5,0.6,0.7    ->      [0.5, 0.6, 0.7]
    range           f1:f2:step          E.g. 0.5:0.7:0.1    ->      [0.5, 0.6, 0.7]
"""


def parse_args(description: str):  # -> Tuple[List[float | int]]
    """
    returns (fault_voltage, fault_width, delay_after_trigger, rounds)
    """
    parser = argparse.ArgumentParser(
        description=description + f"\n{notation_text}",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-fv', '--fault_voltage',
                        type=str,
                        metavar='V',
                        required=True,
                        help='The fault voltage in volts (Notations see above).')
    parser.add_argument('-fw', '--fault_width',
                        type=str,
                        metavar='us',
                        required=True,
                        help='The fault width in microseconds (Notations see above, but ints).')
    parser.add_argument('-dt', '--delay_after_trigger',
                        type=str,
                        metavar='us',
                        nargs='?',
                        default="0",
                        help='The delay after trigger in microseconds (Notations see above).')
    parser.add_argument('-r', '--rounds',
                        type=int,
                        metavar='N',
                        nargs='?',
                        default=10,
                        help='The number of rounds to test each combination.')
    parser.add_argument('-i', '--iterations',
                        type=str,
                        metavar='N',
                        nargs='?',
                        default='1',
                        help='The number of sgx iterations.')
    parser.add_argument('-sv', '--stable_voltage',
                        type=float,
                        metavar='V',
                        nargs='?',
                        default=1.0,
                        help='The stable_voltage in volts.')
    parser.add_argument('-e', '--successive_errors', type=int, metavar='N', nargs='?', default=3,
                        help='Quits round after N successive errors. If 0 is the input it will go through all the rounds.')
    args = parser.parse_args()
    # print(args)
    try:
        args.fault_voltage = convert_args(args.fault_voltage)
        assert isinstance(args.fault_voltage, list) and len(args.fault_voltage) > 0
        fw = convert_args(args.fault_width)
        args.fault_width = [int(i) for i in fw]
        assert isinstance(args.fault_width, list) and len(args.fault_width) > 0
        iter = convert_args(args.iterations)
        args.iterations = [int(i) for i in iter]
        assert isinstance(args.iterations, list) and len(args.iterations) > 0
        dat = convert_args(args.delay_after_trigger)
        args.delay_after_trigger = [int(i) for i in dat]
        assert isinstance(args.delay_after_trigger, list) and len(args.delay_after_trigger) > 0
    except InvalidArgumentException as e:
        help = parser.format_help().replace('\n', '\n\t')
        e.message += f"\n\nThe help menu:\n\t{help}"
        raise e
    return args


def calculate_time(parameters, worst_time=40, best_time=6):
    worst = len(parameters.fault_voltage) * len(parameters.fault_width) * len(
        parameters.delay_after_trigger) * parameters.rounds * worst_time
    best = len(parameters.fault_voltage) * len(parameters.fault_width) * len(
        parameters.delay_after_trigger) * parameters.rounds * best_time
    return convert_time(best), convert_time(worst)


def convert_time(secs: float, pdays=True, time_zone=0) -> str:
    days = int(secs // (24 * 60 * 60))
    secs %= (24 * 60 * 60)
    hours = int(secs // (60 * 60)) + time_zone
    secs %= 60 * 60
    mins = int(secs // 60)
    secs %= 60
    # print(days, hours, mins, secs)
    str = f"{days}d " if pdays else ""
    return f"{str}{hours:02d}:{mins:02d}:{secs:02f}"


def ping_ip(ip: str, duration: int = 2, timeout: float = 10.0) -> bool:
    logger = logging.getLogger("util")
    with subprocess.Popen(f"ping -w {duration} {ip}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
        if 0 == p.wait(timeout):
            logger.debug("connection check: oke")
            return True
        logger.debug("connection check: failed")
        return False


def files_in_dirs(dirs):
    files = []
    for d in dirs:
        dp = pathlib.Path(d)
        if not dp.exists():
            print(f"dir does not exist: {dp}")
            continue
        for f in os.listdir(dp):
            p = pathlib.Path(d, f)
            if not p.exists():
                print(f"path does not exist: {p}")
                continue
            files.append(p)
    return files


def mean(times):
    return numpy.array(times).mean()

def stdev(times):
    return numpy.array(times).std()







if __name__ == "__main__":
    while True:
        c = input("which conversion?")
        if c == 'v':
            v = float(input("Value?"))
            print(f"0x{voltage_to_hex(v)}")
        if c == 'h':
            h = input("Value?")
            print(f"{hex_to_voltage(h)}")
