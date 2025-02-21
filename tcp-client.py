import socket
import sys

def send_messages(outport, ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(('0.0.0.0', int(outport)))
    client.connect((ip, int(port)))
    while True:
        client.sendall(input().encode('utf-8'))
    client.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python tcp_client.py <OUTPORT> <IP> <PORT>")
        sys.exit(1)
    
    outport, ip, port = sys.argv[1], sys.argv[2], sys.argv[3]
    send_messages(outport, ip, port)
