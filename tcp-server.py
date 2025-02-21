import socket
import threading

def handle_client(client_socket, client_address):
    ip, port = client_address
    print(f"{ip}:{port} подключился")

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"{ip}:{port} > {message}")
        except ConnectionResetError:
            break

    client_socket.close()
    print(f"{ip}:{port} отключился")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(5)
    print("Сервер запущен и слушает порт 80...")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()