import struct

f = open('lossy.pcap', 'rb')

# pcap
magic, _, _, _, _, _, llh = struct.unpack('IHHIIII', f.read(24))
assert magic == 0xa1b2c3d4
assert llh == 1

parts = {}
while True:
    # ethernet
    bs = f.read(16)
    if not bs:
        break
    _, _, n, untruncated_length, = struct.unpack('IIII', bs)
    assert n == untruncated_length

    i = 0
    packet = f.read(n)
    assert packet[i+12:i+14] == b'\x08\x00' # IPv4

    # ip
    i = 14
    ihl = packet[i] & 0b1111
    assert packet[i+9] == 6 # TCP

    segment = packet[i+ihl*4:]
    
    
    # tcp
    i = 0
    src_port, dst_port, seq, _, flags = struct.unpack('!HHIIH', segment[i:i+14])
    syn = flags & 0b10 # if the syn flag is 1, then our variable syn will have the value 2 (because 0b10 is 2)
    if src_port != 80 or syn:
        continue

    data_offset = flags >> 12 # 
    parts[seq] = segment[data_offset*4:]

parts = sorted(parts.items())
print(type(parts))
parts = [part[1] for part in parts]
jpeg = b''.join(parts).split(b'\r\n\r\n', 1)[1]
with open('gg.jpeg', 'wb') as w:
    w.write(jpeg)

print("ok")