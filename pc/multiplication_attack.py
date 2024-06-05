from multiprocessing import Process
import time
import util
# from libs import pyboard
import pc.pico_serial as pico_serial
# import pc.ssh as ssh
from udp.hackboard import Hackboard
from constants import *


logger = logging.getLogger("mult")
program = "./HB/multiplication"
print_info = 1
search_term = "Fault"

pico = pico_serial.PicoSerial()

# if not ssh.is_connected():
#     logger.critical("Not connected to hackboard")
#     # pico.send_restart()
#     exit(-1)

with Hackboard(search_term) as hb:
    if hb.communicate(["is-alive"]) != 0:
        logger.critical("HB not on")
        os._exit(-1)
    if hb.start_program(program, print_info) != 0:
        logger.critical("mult not started")
        os._exit(-1)

    time.sleep(2)
    # sudo nice -n -20 ./multiplication

    # Parameters:
    #    - delay_after_trigger,
    #    - nb_of_glitches,
    #    - preparation_voltage,
    #           freq: 1.1GHz -> 1.0
    #                 800MHz -> 0.78
    #    - preparation_width,
    #    - fault_voltage,
    #           freq: 1.1GHz -> 0.71
    #                 800MHz -> 0.52
    #    - fault_width,
    #           Delay is strictly between the packets. So the time needed to send a packet (~50 us per packet) is not included.
    #    - stable_voltage
    # test_sequence = []
    stable_voltage = 0.96
    preparation_voltage = stable_voltage
    preparation_width = 0
    preparation_substract = 0
    # fault_voltage = 0.57
    fault_voltage = 0.50
    fault_width = 49
    fault_substract = 0
    fault_width_substract = 0
    rounds = 100

    logger.info("Start testing")
    while True:
        errors = 0
        for i in range(rounds):
            logger.results(
                f"Round: {i} - voltage: {fault_voltage} (0x{util.voltage_to_hex(fault_voltage)}), width: {fault_width}")
            pico.send_write_voltage(
                util.voltage_to_hex(fault_voltage),
                True, util.voltage_to_hex(stable_voltage),
                fault_width)
            time.sleep(0.5)
            # if not ssh.is_connected():
            if not 0 == hb.communicate(["is-alive"]):
                errors += 1
                logger.results(f"ssh disconnected -> errors: {errors}")
                pico.send_restart()
                if hb.start_program(program, print_info) != 0:
                    logger.critical("mult not restarted")
                    os._exit(-1)
        if errors > 3:
            logger.critical("All errors")
            break
        fault_voltage -= fault_substract
        fault_width -= fault_width_substract
        preparation_voltage -= preparation_substract
        logger.results(f"Rounds completed with {errors} errors")
