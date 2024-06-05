from pathlib import Path


folder = r"C:\Users\gielo\Documents\School\Burgie_master_2\thesis\data\logs\ANALYZED\sgx_iterations"
file = ""

new_iterations = 100

with open(Path(folder, file), 'r') as f:
    lines = f.readlines()

results_search_phrase = "Finished rounds with"

for index, line in enumerate(lines):
    if results_search_phrase in line:        
        # new format
        line = line[:-1] + f', iterations: {new_iterations},\n'

        # increase the rounds by one 
        i = line.find('/') + 1
        j = line.find(' errors', i)
        rounds = int(line[i:j])
        line = line[:i] + f"{rounds + 1}" + line[j:]

        lines[index] = line

with open(Path(folder, file), 'w') as f:
    f.write(''.join(lines))