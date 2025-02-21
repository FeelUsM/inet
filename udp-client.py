import socket
import sys

def send_message(ip, port, message):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(message.encode('utf-8'), (ip, int(port)))
    client.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python udp_client.py <IP> <PORT> <MESSAGE>")
        sys.exit(1)
    
    ip, port, message = sys.argv[1], sys.argv[2], sys.argv[3]
    send_message(ip, port, message)
