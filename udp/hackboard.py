import socket
from typing import List, Tuple
from constants import *

logger = logging.getLogger("HB")
bufsize = 65538


class Hackboard():
    def __init__(self, timeout: float = 10) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(PC_ADDRESS)
        self.sock.settimeout(timeout)
        self.target_addr = HB_ADDRESS

    def is_alive(self) -> bool:
        try:
            data = self._communicate(["ALIVE"])
            if data[-1] != "ACK":
                logger.error("CMD NAK")
                raise Exception("This should not happen")
            if data[0] == "ALIVE":
                logger.debug("HB is ALIVE")
                return True
        except socket.timeout:
            logger.warning("timeout expired during is_alive")
        return False

    def exec_command(self, program: str, background: bool=False) -> Tuple[int, str]:
        try:
            bg = "" if background else "WAIT"
            cmd = ["CMD", program, bg]
            data = self._communicate(cmd)
            if data[-1] != "ACK":
                logger.error("CMD NAK")
                return -1, "NAK"
            if not background and data[0] == "CMD":
                cmd = data[1]
                code = int(data[2])
                output = data[3]
                logger.debug(f"output command: {cmd}, {code}: {output}")
                return code, output
            return 0, "no"
        except socket.timeout:
            logger.warning("timeout expired during exec_command")
        return -1, None

    def get_data(self) -> str:
        try:
            data = self._communicate(["DATA"])
            if data[-1] != "ACK":
                logger.error("DATA NAK")
                return None
            if data[0] == "NODATA":
                logger.debug("no data available")
            if data[0] == "DATA":
                data = data[1].replace("\n", "\t")
                logger.debug(f"data: {data}")
                return data
        except socket.timeout:
            logger.warning("timeout expired during get_data")
        return None

    def _communicate(self, msg: List[str]) -> List[str]:
        msg = SEP.join(msg)
        logger.debug(f"sending {msg}")
        self.sock.sendto(msg.encode(), self.target_addr)
        data = self.sock.recv(bufsize).strip().decode().split(SEP)
        return data


if __name__ == "__main__":
    logger.info("starting hackboard")
    with Hackboard() as hb:
        while True:
            cmd = input("CMD? ").strip()
            if cmd == "Q" or cmd == "q":
                break
            elif len(cmd) > 0:
                hb.exec_command(["cmd", cmd])
