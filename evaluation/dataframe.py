from datetime import datetime
from pathlib import Path
import pandas as pd
import os
import evaluation.sig_eval as sig_eval

results_search_phrase = "Finished rounds with"
block_search_phrase = "Round: "
# dataframe_folder = "dataframes"
fault_str_SGX = "Faulted result\nResult = 1\n"
fault_str_MULT = "Faulted result: "

new_format = True

def get_dataframe(file: Path, type):
    # if not os.path.exists(f"{dataframe_folder}/{file}"):
    # print("calculating df")
    with open(file, 'r') as f:
        lines = f.readlines()
    blocks = create_rounds_blocks(lines)
    df = create_dataframe(blocks, type)
        # df.to_pickle(f"{dataframe_folder}/{os.path.basename(file)}")
    # else:
        # print("loading df from file")
        # df = pd.read_pickle(f"{dataframe_folder}/{file}")
    return df

"""
returns a list of blocks which are all rounds for a parameter combination. The first block contains starting info.
Every block is list of the different rounds in this combination. The first element are the results.
Every round is a str containing all lines from the log file. 
"""
def create_rounds_blocks(lines):
    blocks = [['START: \n']]
    first = True
    for line in lines:
        if results_search_phrase in line:
            blocks[-1].insert(0, line)
            blocks.append([])
        elif block_search_phrase in line:
            if first:
                first = False
                blocks.append([])
            blocks[-1].append(line)
        else:
            if len(blocks[-1]) == 0:
                print(f"Ignored line between rounds: {line}")
            else:
                blocks[-1][-1] += line
    # print(blocks[-2:])
    if len(blocks[-1]) != 0:
        raise AssertionError("Log was probably not ended correctly")
    return blocks[:-1]


def get_section(line: str, start: str, end: str, default=-1):
    i = line.find(start)
    j = line.find(end, i)
    if i == -1 or j == -1:
        l = line.replace('\n', '\\n')
        print(f"Some elements not found: {l}")
        return default
    return line[i + len(start):j].strip()


def get_stats_from_results(line: str):
    if results_search_phrase not in line:
        print(line)
        raise AssertionError("results not in line")
    time_str = line[1:line.find(' - ')].strip()
    rounds_str = get_section(line, "/", " errors")
    crash_str = get_section(line, "crash: ", ",")
    error_str = get_section(line, "error: ", ")")
    v_str = get_section(line, "v: ", ",")
    w_str = get_section(line, "w: ", ",")
    if not new_format:
        dat_str = get_section(line, "dat: ", "\n")
        # iter_str = get_section(line, "iterations: ", ",")
        iter_str = -1
    else:
        dat_str = get_section(line, "dat: ", ",")
        iter_str = get_section(line, "iterations: ", ",")

    timestamp = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S,%f")
    error = int(error_str)
    crash = int(crash_str)
    rounds = int(rounds_str)
    iterations = int(iter_str)
    v = float(v_str)
    w = int(w_str)
    dat = int(dat_str)
    error_percent = error / rounds
    # if error > rounds:
    #     print(error, rounds, timestamp)
    # print(timestamp, error, crash, rounds, iterations, v, w, dat)
    return timestamp, error, crash, rounds, iterations, v, w, dat, error_percent


def create_dataframe(blocks, type):
    if type == 'mult':
        fault_str = fault_str_MULT
    elif type == 'sgx':
        fault_str = fault_str_SGX
    else:
        print("unknown type")
        return None
    timestamps = []
    rounds = []
    iterations = []
    nb_faults = []
    errors = []
    crashes = []
    voltages = []
    widths = []
    dats = []
    faults = []
    regular_rounds = []
    error_percent = []
    fault_percent = []
    regular_percent = []
    for block in blocks[1:]:
        t, e, c, r, it, v, w, d, ep = get_stats_from_results(block[0])
        f = 0
        for round in block[1:]:
            i = round.find(fault_str)
            if i != -1:
                f += 1
                hex_str = round[i + len(fault_str):round.find('\n', i + len(fault_str))]
                faults.append(sig_eval.transform_fault_str(hex_str, type))
        s = r - e - f
        timestamps.append(t)
        rounds.append(r)
        iterations.append(it)
        nb_faults.append(f)
        errors.append(e)
        regular_rounds.append(s)
        crashes.append(c)
        voltages.append(v)
        widths.append(w)
        dats.append(d)
        error_percent.append(ep)
        fault_percent.append(f / r)
        regular_percent.append(s / r)

    # print(faults)
    df_faults = sig_eval.analyze_faults(faults)
    df = pd.DataFrame({'Timestamp': timestamps,
                       'Errors': errors,
                       'Crashes': crashes,
                       'Faults': nb_faults,
                       'Regular Rounds': regular_rounds,
                       'Rounds': rounds,
                       'Iterations': iterations,
                       'Voltages': voltages,
                       'Widths': widths,
                       'Delays After Trigger': dats,
                       'Error Percentage': error_percent,
                       'Fault Percentage': fault_percent,
                       'Regular Percentage': regular_percent,
                       })
    return df.join(df_faults)
