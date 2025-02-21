import socket
import time
import sys
import threading

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

outport = int(sys.argv[1])
print('ваш IP:port')
print(STUN(outport),sep=':')
print('введите IP:port собеседника')
ip, port = input().split(':')
port = int(port)

# отправляет пакет каждую секунду, пока не получит ответ
# потом udp-duplex
connected = False
def sender(sock):
	while not connected:
		sock.sendto(b"hello\n",(ip, port))
		time.sleep(1)
	while True:
		sock.sendto((input()+'\n').encode('utf-8'),(ip,port))

def receiver(sock):
	global connected
	while True:
		data, client_address = sock.recvfrom(1024)
		if not connected:
			print('connected!!!')
		connected = True
		message = data.decode('utf-8')
		print(message,end='')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", outport))
threading.Thread(target=sender, args=(sock,)).start()
threading.Thread(target=receiver, args=(sock,)).start()

# создает слушающий сокет
# каждую секунду пересоздаёт клиентский сокет
# как только 