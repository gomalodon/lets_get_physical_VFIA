import subprocess
import logging
import sys
import threading
from constants import *

# ./injection-code/HB/multiplication 100000000000

logger = logging.getLogger("ssh")


class LogPipe(threading.Thread):
    """
    Pipes the output from the subprocess.stdout into the sys.stdout
    credits to https://stackoverflow.com/questions/21953835/run-subprocess-and-print-output-to-logging
    """

    def __init__(self, level):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.level = level
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe"""
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything."""
        print("hey")
        for line in iter(self.pipeReader.readline, ''):
            logger.log(self.level, line.strip('\n'))
        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe."""
        os.close(self.fdWrite)

    def write(self, message):
        """If your code has something like sys.stdout.write"""
        logger.log(self.level, message)

    def flush(self):
        """If you code has something like this sys.stdout.flush"""
        pass


def communicate(cmd: str, is_ssh: bool = False, log: bool = True, timeout: float = 15.0) -> int:
    base = f"sshpass -p {PASS} ssh {USER}@{IP} -o 'ServerAliveInterval 10' " if is_ssh else ""
    if log:
        logger.info(cmd)
    try:
        sys.stdout = LogPipe(RESULTS_LVL)
        sys.stderr = LogPipe(logging.ERROR)
        ret = -1
        p = subprocess.Popen(base + cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        while is_connected():
            try:
                ret = p.wait(timeout)
                break
            except subprocess.TimeoutExpired:
                logger.warning(f"timeout expired for cmd: {cmd}")

    finally:
        p.kill()
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        logger.debug(f"ssh return code: {ret}")
        return ret


def is_connected(duration: int = 2, timeout: float = 10.0) -> bool:
    with subprocess.Popen(f"ping -w {duration} {IP}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
        if 0 == p.wait(timeout):
            logger.debug("connection check: oke")
            return True
        logger.debug("connection check: failed")
        return False


if __name__ == "__main__":
    logger.info("starting ssh")
    try:
        if not is_connected():
            logger.critical("Not connected to hackboard")
            os._exit(-1)
        while True:
            cmd = input("CMD? ").strip()
            if cmd == "Q" or cmd == "q":
                break
            elif cmd == "mul":
                communicate("./injection-code/HB/multiplication", is_ssh=True)
            elif len(cmd) > 0:
                communicate(cmd, is_ssh=True)
    except KeyboardInterrupt:
        logger.critical("Keyboard Interrupt")
