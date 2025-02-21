import stun
import socket
import sys
import time

def STUN(port, host="stun.ekiga.net"):
    #logging.debug(f"STUN request via {host}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.setblocking(0)
    server = socket.gethostbyname(host)
    work = True
    while work:
        sock.sendto(
            b"\x00\x01\x00\x00!\x12\xa4B\xd6\x85y\xb8\x11\x030\x06xi\xdfB",
            (server, 3478),
        )
        for i in range(20):
            try:
                ans, addr = sock.recvfrom(2048)
                work = False
                break
            except:
                time.sleep(0.01)

    sock.close()
    return socket.inet_ntoa(ans[28:32]), int.from_bytes(ans[26:28], byteorder="big")


local_port = int(sys.argv[1])
print(stun.get_ip_info(source_port=local_port, stun_host="stun.l.google.com"))
print(stun.get_ip_info(source_port=local_port, stun_host="stun1.l.google.com"))
print(stun.get_ip_info(source_port=local_port, stun_host="stun2.l.google.com"))
print(stun.get_ip_info(source_port=local_port, stun_host="stun3.l.google.com"))
print(STUN(local_port))
