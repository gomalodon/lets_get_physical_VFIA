import os

# folder = "important_logs/"
# folder = "logs/"
folder = "local_logs/"
files = ["subprocess-2024-05-06-13-13-51.log"]
# files = os.listdir(folder)

strip_time = False

levels = [
    # "DEBUG",
    # "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "RESULTS"
]

terms = [
    # "Round",
    "meh",
    "Nooo",
    "Result = 0",
    "signature"
]

only_line = [
    # "Time of writing voltage",
    # "Time:"
]

# TODO make not exclusive
exclude = [
    "0x2d, 0x3e, 0x35, 0x4d, 0x6d, 0xb7, 0xf1, 0xd2, 0x32, 0xce, 0x81, 0x52, 0x19, 0x75, 0xc2, 0x7b, 0x4f, 0xc1, 0x3a, 0x2f, 0x97, 0xdb, 0x48, 0x04, 0xb4, 0xae, 0x95, 0xd0, 0x87, 0x3e, 0xfb, 0x82, 0xf9, 0x92, 0xe3, 0x1b, 0x59, 0x11, 0x58, 0x43, 0x21, 0x41, 0x02, 0xd5, 0x69, 0x28, 0x8d, 0xb4, 0x9a, 0xd2, 0xaa, 0x2b, 0x36, 0xc1, 0xb7, 0xa1, 0xb4, 0x28, 0x77, 0xf4, 0x4f, 0xfe, 0xdc, 0x4c, 0xdb, 0x2d, 0x9a, 0x83, 0x0e, 0xe1, 0x8a, 0xff, 0xb3, 0xc2, 0xc9, 0x25, 0xfb, 0xdc, 0x3e, 0xf9, 0xaf, 0xf5, 0x26, 0x46, 0xc0, 0xb2, 0xe0, 0xd7, 0x84, 0x1f, 0x25, 0xb4, 0x8b, 0x2e, 0x1b, 0xc3, 0x67, 0x52, 0xf5, 0xa8, 0xee, 0xf1, 0x68, 0x5c, 0x7d, 0xd8, 0xdc, 0x26, 0x0b, 0x31, 0x82, 0xca, 0xe2, 0x45, 0x4b, 0x50, 0x29, 0xe3, 0x50, 0x63, 0x00, 0xe3, 0xe9, 0xac, 0x19, 0x7a, 0xeb",
    # "MULT OUTPUT: Running"
]

search = levels + terms
print("search terms:", search)
print("one line search terms:", only_line)
print("exclude terms:", exclude)

def append_result(line):
    if strip_time and line.startswith("["):
        line = line[line.find("]") + 2:]
    results.insert(0, line)

for file in files:
    results = []
    file = f"{folder}/{file}"

    with open(file) as f:
        f = f.readlines()

    buff = ""
    i = len(f) - 1
    while i >= 0: 
        line = f[i]
        for term in only_line:
            if term in line:
                append_result(line)
        if not line.startswith("["):
            buff = line + buff
        else:
            line = line + buff
            buff = ""
            for phrase in search:
                if phrase in line:
                    append_result(line)
                    break
        i -= 1
    results.insert(0, f"{file}\n\n")

    i = len(results)-1
    while i >= 0:
        sub = False
        for ex in exclude:
            # print(results[i].find(ex))
            # print(results[i] + '\n')
            # print(i)
            if results[i].find(ex) >= 0:
                results.pop(i)
                i -= 1
                sub = True
        if not sub:
            i -= 1

    if len(results) == 0:
        print("No results")
    else:
        print("".join(results))
    print("===================================")    