# https://docs.micropython.org/en/latest/reference/pyboard.py.html
# https://github.com/micropython/micropython/blob/master/tools/pyboard.py

import logging
from typing import List
from constants import *
from libs import pyboard
from contextlib import contextmanager

logger = logging.getLogger("pico")


# @contextmanager
# def pico_connection(func_import: bool = True):
#     pico = pyboard.Pyboard(PICO_PORT)
#     try:
#         pico.enter_raw_repl()
#         if func_import:
#             pico.exec('from functions import *')
#         yield pico
#     finally:
#         pico.exit_raw_repl()
#         pico.close()


# global STARTED
# STARTED = False
# startup_script = """
# from functions import *
# import _thread
# global voltage
# voltage = None
# _thread.start_new_thread(led_on, ())
# # led_on()
# """


# def startup():
#     global STARTED
#     logger.info("Running startup script on pico")
#     with pico_connection() as pico:
#         # pico.exec(startup_script)
#         STARTED = True


# def send(cmd: str | bytes) -> None:
#     # global STARTED
#     # assert STARTED
#     pico.exec(cmd)


files_to_upload = [PICO_PATH + "functions.py", PICO_PATH + "main.py"]


def upload_files(path: List[str] = files_to_upload) -> None:
    # with pico_connection(False) as pico:
    assert pico.fs_exists
    logger.info(f"Previous files on pico: {[(i.name, i.st_size) for i in pico.fs_listdir()]}")
    for f in path:
        pico.fs_put(f, "/" + f.split('/')[-1])
    logger.info(f"Current files on pico: {[(i.name, i.st_size) for i in pico.fs_listdir()]}")


def remove_file(file: str) -> None:
    # with pico_connection(False) as pico:
    assert pico.fs_exists
    logger.info(f"Removing on pico: {file}")
    pico.fs_rm(file)


if __name__ == '__main__':
    logger.info("starting pico")
    # startup()
    try:
        pico = pyboard.Pyboard(PICO_PORT)
        pico.enter_raw_repl()
        pico.exec('from functions import *')
        while True:
            cmd = input("CMD? ").strip()
            if cmd == "Q" or cmd == "q":
                break
            elif cmd == "upload":
                upload_files()
            elif len(cmd) > 0:
                logger.info(pico.exec(cmd))
    except KeyboardInterrupt:
        logger.critical("Keyboard Interrupt")
    finally:
        pico.exit_raw_repl()
        pico.close()
