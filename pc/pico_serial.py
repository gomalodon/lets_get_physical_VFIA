import time
import util
import serial
from constants import *

logger = logging.getLogger("pico")

"""
s\x07\xd0 v\x1d\x01\x1d\x00\x00
73 07 d0 76 1d 01 1d 00 00

s\x07\xd0ls -la\n v\x1d\x01\x1d\x00\x00\x00\x00
73 07 d0 6c 73 20 2d 6c 61 0a 76 1a 01 1d 00 00 00 50

73 00 00 6c 73 0a 76 1a 01 1d 00 00 00 50
"""


class PicoSerial:
    def __init__(self, fd: str = PICO_PORT) -> None:
        self.ser = serial.Serial(fd, 115200)
        logger.info("Started pico serial")

    def _write(self, buff: bytes, ack: bool = True) -> bytes:
        """
        buff: the message to send
        ack: wait for response from pico
        """
        # logger.debug(f"Resetting buffers (in: {self.ser.in_waiting}, out: {self.ser.out_waiting})")
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        logger.debug(f"Writing: {buff}")
        self.ser.write(buff)
        if ack:
            out = self.ser.read_until(b"Done\r\n").strip().decode()
            out = out.replace('\r\n', '\r')
            logger.debug(f"pico output: {out}")
            return out
        return None

    def send_write_voltage(self, voltage: str, trig: bool = False, ret_value: str = "1d", delay: int = 0) -> bytes:
        """
        Delay is strictly between the packets. So the time needed to send a packet (~50 us per packet) is not included.
        """
        buff = b'v'
        buff += bytes.fromhex(voltage)
        buff += b'\1' if trig else b'\0'
        if ret_value is None:
            buff += b'\0'
        else:
            buff += bytes.fromhex(ret_value)
            buff += delay.to_bytes(4, 'big')
        return self._write(buff)

    def send_command(self, command: str, keep_waiting: bool = True) -> bytes:
        if not command.endswith('\n'):
            command += '\n'
        if len(command) > 64:
            logger.error(f"Command can be maximum 64 bytes: {command}")
        if command.startswith('s'):
            w = '1' if keep_waiting else '2'
            command = 's' + w + command[1:]
        return self._write(('c' + command).encode())

    def starting_and_glitching(
            self, program: str, delay_after_trigger: int, voltage: str, trig: bool = False, ret_value: str = "1d",
            glitch_delay: int = 0, keep_waiting: bool = True) -> bytes:
        w = b'1' if keep_waiting else b'2'
        self._write(b's' + delay_after_trigger.to_bytes(4, 'big') + w + program.encode() + b'\n', ack=False)
        logger.info(f"Pico will wait for {delay_after_trigger}us")
        t1 = time.time_ns()
        output = self.send_write_voltage(voltage, trig, ret_value, glitch_delay)
        output = output.replace('\r', '\n')
        print(output)
        i = output.find("Time diff between start and voltage:")
        us_diff = int(output[i + 36:output.find(' us', i)])
        print(t1, us_diff)
        logger.info(f"Time of writing voltage: ~{util.convert_time((t1 + us_diff * 1000)/1e9, False, 2)}")
        i = output.find("UART RETURN")
        serial_output = output[i:output.find('\n', i)]
        # print(serial_output)
        ser_split = serial_output.split('\\|\\')
        code = int(ser_split[1])
        ser_output = ser_split[2].replace('\\n', '\n').strip()
        output = output.replace('\\n', '\n').strip()
        logger.info(f"Output: {output}")
        logger.debug(f"HB code: {code}, output:\n{ser_output}")
        return code, ser_output

    def send_blink(self, nb: int) -> bytes:
        return self._write(b'b' + nb.to_bytes(1, "big"))

    def send_led(self, on: int) -> bytes:
        return self._write(b'l' + on.to_bytes(1, "big"))

    def send_trigger(self) -> bytes:
        return self._write(b't')

    def send_on_off(self) -> bytes:
        return self._write(b'o')

    def send_restart(self) -> bytes:
        return self._write(b'r')

    # def send_set_global_voltage(self, voltage: str) -> None:
    #     self._write(b'g' + bytes.fromhex(voltage))


if __name__ == "__main__":
    # pico = PicoSerial()
    pico = PicoSerial(PICO_PORT)
    while True:
        cmd = input("CMD? ").strip()
        if cmd == "Q" or cmd == "q":
            break
        if len(cmd) > 0:
            if cmd[:1] == "v":
                fv, trig, rv, w = cmd[1:3], cmd[3:4], cmd[4:6], int(cmd[6:])
                print(
                    f"Writing: fault voltage: {util.hex_to_voltage(fv)} (0x{fv}), return voltage: {util.hex_to_voltage(rv)} (0x{rv}), trigger: {trig}, width: {w}")
                print(pico.send_write_voltage(fv, trig, rv, w))
            elif cmd[:1] == "w":
                for i in range(100):
                    fv, trig = "03", True
                    print(f"Writing single fault voltage: {util.hex_to_voltage(fv)} (0x{fv})")
                    print(pico.send_write_voltage(fv, trig, None))
                    # print(pico.send_write_voltage(fv, trig, None))
                    time.sleep(0.5)
            elif cmd[:1] == "b":
                print(pico.send_blink(int(cmd[1:])))
            elif cmd[:1] == "l":
                print(pico.send_led(int(cmd[1:])))
            elif cmd[:1] == "t":
                print(pico.send_trigger())
            elif cmd[:1] == "o":
                print(pico.send_on_off())
            elif cmd[:1] == "r":
                print(pico.send_restart())
            elif cmd[:1] == "s":
                code, output = pico.starting_and_glitching(
                    program=cmd[1:],
                    delay_after_trigger=2000,
                    voltage=util.voltage_to_hex(0.50),
                    trig=True,
                    glitch_delay=200)
                print(f"ret: {code}, {output}")
            elif cmd[:1] == "c":
                print(pico.send_command(cmd[1:]))
            elif cmd[:1] == "i":
                command = input("command: ")
                data = input("data: ")
                buff = b'i'
                buff += bytes.fromhex(command)
                buff += bytes.fromhex(data)
                buff += b'\1'
                print(pico._write(buff))
            # elif cmd[:1] == "g":
            #     pico.send_set_global_voltage(cmd[1:])
