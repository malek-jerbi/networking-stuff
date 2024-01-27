import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(('0.0.0.0', 9999))


while True:
    data , sender = s.recvfrom(4096)
    response = data.upper()
    s.sendto(response, sender)
