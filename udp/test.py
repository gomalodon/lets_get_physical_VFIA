#/usr/bin/env/python3 
#Python UDP Listener, listening on localhost 1025, change address 
# to listen on other ip/port combos. 
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 6665))
while True:
    print("listening")
    data, address = sock.recvfrom(65538)
    text = data.decode('ascii')
    print('Connection from Client{} says {}'.format(address, text))
    text = 'Your data was {} bytes long'.format(len(data))
    data = text.encode('ascii')
    sock.sendto(data, address)
