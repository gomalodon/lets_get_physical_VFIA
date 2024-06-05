import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)
# sock.bind(('0.0.0.0', 6666))
address = ("192.168.10.1", 6666)
has_acked = False

sock.sendto("udp-connect".encode(), address)
while True:
    try:
        data = sock.recv(65538)
        if data.strip() == b"ACK":
            has_acked = True
        print(data.strip())   
    except TimeoutError:
        if not has_acked:
            print("resending connect")
            sock.sendto("udp-connect".encode(), address)
        pass