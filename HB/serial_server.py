import os
import subprocess
import serial

if os.name == 'nt':
    PORT = "COM7"
else:
    PORT = "/dev/ttyUSB0"

ser = serial.Serial(PORT, 115200)

p_mult = None
# mult = "taskset --cpu-list 1 /home/hackboard/HB/multiplication 0"
# p_mult = subprocess.Popen(mult, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

msg = None
print("Listening...")
while True:
    try:
        # print(f"Resetting buffers (in: {ser.in_waiting}, out: {ser.out_waiting})")
        # ser.reset_input_buffer()
        # ser.reset_output_buffer()
        cmd = ser.read(1).decode()
        print(f"CMD: {cmd}")
        if cmd == 'c':
            data = ser.read_until(b'\n').strip().decode()
            print(f"Data: {data}")
        elif cmd == 's':
            keep_waiting = False if ser.read(1) != b'1' else True
            print("keep_waiting:", keep_waiting)
            program = ser.read_until(b'\n').strip().decode()
            print(f"Running: {program}")
            
            out_pipe = subprocess.PIPE if keep_waiting else open('sgx.log', 'ab')
            p = subprocess.Popen(program, shell=True, stdout=out_pipe, stderr=subprocess.STDOUT)
            if keep_waiting:
                code = p.wait()
                output = p.stdout.read().replace(b'\n', b'\\n')
                if p_mult:
                    pcode = p_mult.returncode if p_mult.returncode else "Running"
                    output += f"MULT OUTPUT: {pcode}".encode()
                    try:
                        outs, _ = p_mult.communicate(timeout=0.1)
                        output += outs.replace(b'\n', b'\\n')
                    except subprocess.TimeoutExpired:
                        pass
                msg = code.to_bytes(1, 'big') + output + b'\n'
        elif cmd == 'r':
            if msg:
                print(f"Writing: {msg}")
                ser.write(msg)
                msg = None
            else:
                print("msg not assigned")
                ser.write((-1).to_bytes(1, "big") + b"Msg not assigned\n")
    except Exception as e:
        print(f"Exception: {e}")