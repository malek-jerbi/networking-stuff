import select
import socket


listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setblocking(False)

listener.bind(('0.0.0.0', 10001))
listener.listen(10)

inputs = [listener]
outputs = []
to_send = set()

while True:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for s in readable:
        if s is listener:
            # listener can accept connection immediately
            client_sock, client_addr = s.accept()
            client_sock.setblocking(False)
            inputs.append(client_sock)
        else:
            # socket is a client connection
            data = s.recv(4096)
            if data:
                print(data)
                outputs.append(s)
                to_send.add(s)
            else:
                s.close()
            inputs.remove(s)
    for s in writable:
        if s in to_send:
            to_send.remove(s)
            outputs.remove(s)
            s.send(b'HTTP/1.0 200 ok\r\n\r\nhi!')
            s.close()