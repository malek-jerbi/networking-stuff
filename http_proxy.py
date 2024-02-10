import socket
import json
from http_parser import HttpRequest, HttpState


def should_keepalive(req: HttpRequest):
    cn = req.headers.get(b"connection")
    if req.version == b"HTTP/1.0":
        return cn and cn.lower() == b"keep-alive"
    if req.version == b"HTTP/1.1":
        return not (cn and cn.lower() == b"close")
    
def handle_client_connection(client_socket):
    while True:
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upstream_sock.connect(("127.0.0.1", 8000))
        print("Connected to 127.0.0.1")

        req = HttpRequest()
        close = False
        while req.state is not HttpState.END:
            data = client_socket.recv(4096)
            if not data:
                close = True
                break
            req.parse(data)
            print(f"sending {len(data)}B")
            upstream_sock.send(data)
            print("sent")
        if close:
            upstream_sock.close()
            break

        while True:
            new_data = upstream_sock.recv(4096)
            if not new_data:
                break
            print(f"received response: {len(new_data)}B")
            print(f"now forwarding that response back to the first connection ({addr})")
            conn.send(new_data)
            print("sent")

        upstream_sock.close()

        if not should_keepalive(req):
            return

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    PORT = 6001
    s.bind(("0.0.0.0", PORT))

    s.listen(10)
    print(f"listening to connections on port {PORT}")


    while True:
        try:
            conn, addr = s.accept()
            print(f"new connection from {addr}")
            handle_client_connection(conn)
            

        except ConnectionRefusedError:
            conn.send(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            print("bad gateway")
        except Exception as e:
            print(e)
            conn.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')
        finally:
            conn.close()
    s.close()