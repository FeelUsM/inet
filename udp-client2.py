import socket
import sys

def send_message(outport, ip, port, message):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(('0.0.0.0', int(outport)))  # Привязываем клиент к порту 60606
    client.sendto(message.encode('utf-8'), (ip, int(port)))
    client.close()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Использование: python udp_client.py <OUTPORT> <IP> <PORT> <MESSAGE>")
        sys.exit(1)
    
    outport, ip, port, message = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    send_message(outport, ip, port, message)
