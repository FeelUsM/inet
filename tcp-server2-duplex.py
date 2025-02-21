import sys
import socket
import threading

def handle_client(client_socket, client_address):
    print(f"{client_address[0]}:{client_address[1]} подключился")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"{client_address[0]}:{client_address[1]} > {message}",end='')
    except ConnectionResetError:
        pass
    finally:
        print(f"{client_address[0]}:{client_address[1]} отключился")
        client_socket.close()

def handle_keyboard(client):
    print('listen keyboard')
    try:
        while True:
            client.sendall((input()+'\n').encode('utf-8'))
    except:
        client.close()

def start_server(port=80):
    host='0.0.0.0'
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Сервер слушает {host}:{port}")
    
    client_socket, client_address = server.accept()
    threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
    threading.Thread(target=handle_keyboard, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server(int(sys.argv[1]))
