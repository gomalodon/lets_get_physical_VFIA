import re
from pathlib import Path
from evaluation.dataframe import create_rounds_blocks, get_stats_from_results
from util import files_in_dirs


folder = r"C:\Users\gielo\Documents\School\Burgie_master_2\thesis\data\logs\ANALYZED"
dest_dir = r"evaluation\output"
filename_all_strs = r'all_unique_strs.log'

subfolders = ["mult_iterations", "sgx_iterations", "other", "10 test", "10 test - switched"]

filter_data = True
no_pattern_replacements = True
replace_analyzed_files = False

patterns = {
    r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{9}\]': '[TIME]',
    r'Operands: (\d+) == (\d+)': 'Operands: OP1 == OP2',
    r'Info: [0-9]+ =\?= [0-9]+ for [0-9]+ and [0-9]+': 'Info: M1 =?= M2 for OP1 and OP2',
    r'Waiting (\d+) us': 'Waiting DELAY us',
    r'Time: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{9}': 'Time: TIME',
    r'Started [0-9]+ decryptions': 'Started N decryptions',
    r'\./sgx-script\.sh: line 10: [0-9]+': './sgx-script.sh: line 10: ERR',
    r'Starting [0-9]+ multiplications...': 'Starting N multiplications...',
    r'Starting multiplications...': '',
    r'Done': '',
    r'Running': '',
    r'Exiting...': '',
    r'Creating enclave... Hello World init RSA... Init P... Init Q...Successfully made init rsa Now computing inside SGX...': '',
    r'meh - all fine': '',
    r'Result = 1': '',
    r'time delay: [0-9]+': '',
    r'cpu: [0-9]': '',
    r'type: \b(one|loop|iteration)\b': '',
    r'taskset\s+-c\s+\$\d+\s+\./sgx-test/crt_rsa/app\s+\$\d+\s+\$\d+': '',
}

data_patterns = {
    r'0x[0-9a-z][0-9a-z], ': '',
    r'Fault found: [0-9]+ =/= [0-9]+ for [0-9]+ and [0-9]+': 'Fault found: F1 =/= F2 for OP1 and OP2'
}

uart_ret_str = "UART RETURN"
uart_done_str = "Done"
sep = "\\|\\"
mult_split = "MULT OUTPUT: "


def filter_specifics(input_str: str) -> str:
    filtered_str = re.sub(r'\s+', ' ', input_str).strip()
    filtered_str = re.sub(r'\\n', ' ', filtered_str)
    if filter_data:
        patterns.update(data_patterns)
    for k, v in patterns.items():
        if no_pattern_replacements:
            v = ''
        filtered_str = re.sub(k, v, filtered_str)
    filtered_str = re.sub(r'\s+', ' ', filtered_str).strip()
    return filtered_str


def write_to_file(path: Path, unique_strs: set) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    with open(path, 'w') as f:
        unique_lst = sorted(unique_strs)
        for i in unique_lst:
            f.write(f"{i}\n")


def read_analyzed_file(file: Path) -> set:
    with open(file, 'r') as f:
        lines = f.readlines()
        return set([i.strip() for i in lines])

all_unique_strs = set()
files = files_in_dirs([rf"{folder}\{i}" for i in subfolders])

for filename in files:
    filepath = filename.relative_to(folder)
    out_path = Path(dest_dir, filepath)
    if replace_analyzed_files or not out_path.exists():
        print(f"Reading: {filename}")

        unique_strs = set()
        with open(filename) as f:
            lines = f.readlines()
        blocks = create_rounds_blocks(lines)
        # print(blocks[0])
        for block in blocks[1:]:
            # print(block[0])
            stats = get_stats_from_results(block[0])
            for round in block[1:]:
                i = round.find(uart_ret_str)
                j = round.find(uart_done_str, i)
                if i == -1:
                    # print(round, block)
                    print(f"uart_ret_str not found")
                    continue
                _, code, output = round[i:j + len(uart_done_str)].split(sep)
                lst = output.split(mult_split)
                assert len(lst) <= 2
                lst[0] = f"TARGET: {code} {lst[0]}"
                if len(lst) == 2:
                    lst[1] = f"MULT: {lst[1]}"
                for out in lst:
                    unique_str = filter_specifics(out)
                    unique_strs.add(unique_str)

        write_to_file(out_path, unique_strs)
        all_unique_strs.update(unique_strs)
    else:
        print(f"Skipping: {filename}")
        all_unique_strs.update(read_analyzed_file(out_path))

write_to_file(Path(dest_dir, filename_all_strs), all_unique_strs)

print("\n\nDONE")