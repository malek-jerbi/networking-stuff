import socket
import json



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(("0.0.0.0", 4123))

s.listen()
print("listening to connectionson port 4123")

while True:
    conn, addr = s.accept()
    print(f"new connection from {addr}")
    data = conn.recv(4096)
    headers, body = data.split(b'\r\n\r\n')
    d = {}
    print("get .. :", headers.split(b'\r\n')[0])
    for hline in headers.split(b'\r\n')[1:]:
        k, v = hline.split(b': ')
        d[k.decode('ascii')] = v.decode('ascii')

    
    conn.send(b'HTTP/1.1 200 ok\r\n\r\n')
    conn.send(json.dumps(d, indent=4).encode('ascii'))
    #conn.send()
    conn.close()
        