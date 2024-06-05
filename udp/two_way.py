import socket
import subprocess
import time
import traceback


SEP = "\\|\\"
BROADCAST_FILE = "/home/hackboard/udp/broadcast-log"
HB_ADDRESS = ("192.168.0.124", 6666)
buffsize = 65538
file = open(BROADCAST_FILE, "r")
file.seek(0, 2)


def handle(data, addr, sock) -> None:
    i = 0
    msg = []
    while i < len(data):
        if data[i] == "DATA":
            line = file.readline()
            buff = ""
            while line:
                # print(line)
                buff += line
                line = file.readline()
            if len(buff) > 0:
                msg.append("DATA")
                msg.append(buff)
            else:
                msg.append("NODATA")
        elif data[i] == "CMD":
            i += 1
            p = subprocess.Popen(data[i], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            msg.append("CMD")
            msg.append(f"{data[i]}")
            i += 1
            if data[i] == "WAIT":
                p.wait()
                msg.append(f"{p.returncode}")
                msg.append(f"{p.stdout.read()}")
        elif data[i] == "ALIVE":
            msg.append("ALIVE")
        i += 1
    msg.append("ACK")
    msg = SEP.join(msg)
    print(f"SENDING: {msg}")
    sock.sendto(msg.encode(), addr)


def comms():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(HB_ADDRESS)
    while True:
        try:
            data, addr = sock.recvfrom(buffsize)
            data = data.decode().strip().split(SEP)
            print(f"{addr}: {data}")
            handle(data, addr, sock)
        except Exception as e:
            print(e)
            traceback.print_exc()
            sock.sendto("NAK".encode(), addr)


if __name__ == "__main__":
    print("Starting...")
    comms()
