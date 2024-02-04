import socket
import json



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

PORT = 6001
s.bind(("0.0.0.0", PORT))

s.listen()
print(f"listening to connections on port {PORT}")

while True:
    conn, addr = s.accept()
    print(f"new connection from {addr}")

    data = conn.recv(4096)


    upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upstream_sock.connect(("127.0.0.1", 9000))
    print("Connected to 127.0.0.1")
    print(f"sending {len(data)}B")
    upstream_sock.send(data)
    print("sent")

    while True:
        new_data = upstream_sock.recv(4096)
        if not new_data:
            break
        print(f"received response: {len(new_data)}B")
        print(f"now forwarding that response back to the first connection ({addr})")
        conn.send(new_data)
        print("sent")

    upstream_sock.close()
    conn.close()
s.close()