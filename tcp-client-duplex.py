import socket
import sys
import threading

def send_messages(client):
    try:
        while True:
            client.sendall((input()+'\n').encode('utf-8'))
    except:
        client.close()

def receive_messages(client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message,end='')
    except:
        print('>>> disconnected')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python tcp_client.py <OUTPORT> <IP> <PORT>")
        sys.exit(1)
    
    outport, ip, port = sys.argv[1], sys.argv[2], sys.argv[3]
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(('0.0.0.0', int(outport)))
    client.connect((ip, int(port)))

    threading.Thread(target=send_messages, args=(client,)).start()
    threading.Thread(target=receive_messages, args=(client,)).start()
