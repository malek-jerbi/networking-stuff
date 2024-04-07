import sys
import socket
import struct


MAX_PAYLOAD_SIZE = 4
TIMEOUT_INTERVAL = 3


def pack_segment(seq, ack, payload):
    return struct.pack('!HH', seq, ack) + payload
def unpack_segment(data):
    return struct.unpack('!HH', data[:4]), data[4:]

class ReliableDelivery(object):
    def __init__(self, target_addr=None):
        self.target_addr = target_addr
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(TIMEOUT_INTERVAL)
        self.seq = 0
        self.ack = 0
        self.their_ack = 0
        self.pending_payloads = []

    def bind(self, own_addr):
        self._sock.bind(own_addr)

    def send(self, data):
        i = 0
        while i < len(data):
            payload = data[i:i+MAX_PAYLOAD_SIZE]
            segment = pack_segment( self.seq, self.ack, payload)
            while self.their_ack <= self.seq:
                self._sock.sendto(segment, self.target_addr)
                self._wait_for_them()
            self.seq += 1
            i += len(payload)
        pass

    def recv(self):
        while not self.pending_payloads:
            self._wait_for_them()
        return self.pending_payloads.pop(0)
    
    def _wait_for_them(self):
        while True:
            try:
                data, sender = self._sock.recvfrom(4096)
            except socket.timeout:
                break
            if not self.target_addr:
                self.target_addr = sender
            if self.target_addr != sender:
                continue
            (seq, ack), payload = unpack_segment(data)

            # if received ack is higher, update our measure of their_ack
            self.their_ack = max(self.their_ack, ack)
            # if the received seq is expected or older, send (or re-send) an ack
            if payload and seq <= self.ack:
                # if the seq is expected nex in sequence, allow it to be recvd
                if payload and seq == self.ack:
                    self.pending_payloads.append(payload)
                    self.ack += 1

                segment = pack_segment(self.seq, self.ack, b'')
                self._sock.sendto(segment, self.target_addr)
            break


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # we cas as client, and send data to given port
        rd = ReliableDelivery(('127.0.0.1', int(sys.argv[1])))
        rd.send(b'0123456789'*20)
    else :
        rd = ReliableDelivery()
        rd.bind(('0.0.0.0', 8000))
        recvd = 0
        # we act as server, so bind to a port
        while True:
            print(rd.recv())
            # recvd += 1
        rd.send(b'abcd')