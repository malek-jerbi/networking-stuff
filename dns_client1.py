import sys
import socket
import struct



if __name__ == '__main__':
    hostname = sys.argv[1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    id = 42
    flags = 0x0100
    query = struct.pack("!HHHHHH", id, flags,1,0,0,0)
    query += b''.join(len(p).to_bytes(1, 'big') + p.encode('ascii') for p in hostname.split('.')) + b'\x00'
    query += struct.pack('!HH', 1, 1)
    s.sendto(query, ('8.8.8.8', 53))
    print('ok')

    data, sender = s.recvfrom(4096)
    print(data)
    print(sender)
