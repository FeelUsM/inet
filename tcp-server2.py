import socket
import threading

def handle_client(client_socket, client_address):
    print(f"{client_address[0]}:{client_address[1]} подключился")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"{client_address[0]}:{client_address[1]} > {message}")
    except ConnectionResetError:
        pass
    finally:
        print(f"{client_address[0]}:{client_address[1]} отключился")
        client_socket.close()

def start_server(host='0.0.0.0', port=80):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Сервер слушает {host}:{port}")
    
    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    start_server()
