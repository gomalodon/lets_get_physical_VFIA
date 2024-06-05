import select
import time
import socket

FD = "/home/hackboard/udp/broadcast-log"


def follow():
    global sock
    file = open(FD, "rb")
    file.seek(0, 2)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.5)
            if select.select([sock], [], [], 0)[0]:
                wait_for_connection()
            continue
        yield line


def wait_for_connection():
    global address, sock
    req, addr = sock.recvfrom(65538)
    print(f"received {req.decode()} from address {addr}")
    if req.decode().strip() != "udp-connect":
        sock.sendto("connect first".encode(), addr)
        return
    address = addr
    sock.sendto("ACK".encode(), address)


if __name__ == "__main__":
    global address, sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 6666))

    print("starting listening")
    while True:
        wait_for_connection()
        if address:
            for line in follow():
                sock.sendto(line, address)
