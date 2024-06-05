import logging
from datetime import datetime
import os

USER = "hackboard"
IP = "192.168.0.124"
PASS = "HB2"
ITERATIONS = 100000000

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + "/"
HB_DIR = "./HB/"
PICO_PATH = ROOT_DIR + "pico/"

SEP = "\\|\\"
BROADCAST_FILE = "/home/hackboard/udp/broadcast-log"
PC_ADDRESS = ("0.0.0.0", 6666)
HB_ADDRESS = (IP, 6666)

HB_SCRIPT_DELAY = 0

if os.name == 'nt':
    PICO_PORT = "COM4"
else:
    PICO_PORT = "/dev/ttyS4"

LOG = ROOT_DIR + f"logs/subprocess-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"
if os.path.exists(LOG):
    raise Exception(f"Logfile \"{LOG}\" already exists")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG),
        logging.StreamHandler()
    ]
)


def results(self, msg, *args, **kwargs):
    if self.isEnabledFor(RESULTS_LVL):
        self._log(RESULTS_LVL, msg, args, **kwargs)


RESULTS_LVL = 100
logging.addLevelName(RESULTS_LVL, "RESULTS")
logging.Logger.results = results

logger = logging.getLogger()
logger.info(f"logger started @ {LOG}")
