import io
from enum import Enum, auto


class HttpState(object):
    START = auto()
    HEADERS = auto()
    BODY = auto()
    END = auto()

class HttpRequest:
    def __init__(self):
        self.headers = {}
        self.state = HttpState.START
        self.body = b''
        self.residual = b''

    def parse(self, data):
        print("Parsing...", data)
        bs = io.BytesIO(self.residual + data)
        self.residual = b''
        if self.state is HttpState.START:
            request_line = bs.readline()
            if request_line[-1:] != b'\n':
                self.residual = request_line
                return
            self.method, self.uri, self.version = request_line.rstrip().split(b" ")
            self.state = HttpState.HEADERS

        if self.state is HttpState.HEADERS:
            while True:
                field_line = bs.readline()
                if not field_line:
                    break
                if field_line[-1:] != b'\n':
                    self.residual = field_line
                    return
                if field_line == b"\r\n" or field_line == b'\n':
                    if self.method == b"GET":
                        self.state = HttpState.END
                    else:
                        self.state = HttpState.BODY
                    break

                key, value = field_line.rstrip().split(b": ")
                self.headers[key.lower()] = value
        
        if self.state is HttpState.BODY:
            self.body += bs.read()
        


if __name__ == "__main__":
    req = HttpRequest()
    assert req.state is HttpState.START
    req.parse(b"GET / HTTP/1.0\r\nUser-agent: test\r\nFoo: bar\r\n\r\n")
    assert req.method == b"GET"
    assert req.version == b"HTTP/1.0"
    assert req.headers[b"user-agent"] == b"test"
    assert len(req.headers) == 2

    # Progressive Parsing
    req = HttpRequest()
    assert req.state is HttpState.START
    req.parse(b"GET / ")
    req.parse(b"HTTP/1.0\r\n")
    assert req.state is HttpState.HEADERS
    req.parse(b"User-agent: ")
    req.parse(b"test\r\nFoo: bar\r\n\r\n")
    assert req.method == b"GET"
    assert req.version == b"HTTP/1.0"
    assert req.headers[b"user-agent"] == b"test"
    assert len(req.headers) == 2

    req = HttpRequest()
    req.parse(b"POST / HTTP/1.0\r\n\r\nfoo")
    req.parse(b'bar')
    assert req.state == HttpState.BODY
    assert req.body == b"foobar"

    req = HttpRequest()
    req.parse(b"GET / HTTP/1.1\r\r\n\r\nfoo")
    assert req.state == HttpState.END
    assert req.body == b""
    print("ok")