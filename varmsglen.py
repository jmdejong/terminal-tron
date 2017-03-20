
HEADER_SIZE = 4


def send(sock, msg):
    length = len(msg)
    header = length.to_bytes(4, byteorder="big")
    totalmsg = header + msg
    #totallength = length + 4
    sock.sendall(totalmsg)
    #totalsent = 0
    #while totalsent < totallength:
        #sent = sock.send(totalmsg[totalsent:])
        #if sent == 0:
            #raise RuntimeError("socket connection broken")
        #totalsent = totalsent + sent

def receive(sock):
    header = sock.recv(4)
    length = int.from_bytes(header, byteorder="big")
    chunks = []
    bytes_recd = 0
    while bytes_recd < length:
        chunk = sock.recv(min(length - bytes_recd, 4096))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    return b''.join(chunks)

