import socket

def start_server(host='0.0.0.0', port=808):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))
    print(f"Сервер слушает {host}:{port}")
    
    while True:
        data, client_address = server.recvfrom(1024)
        message = data.decode('utf-8')
        print(f"{client_address[0]}:{client_address[1]} > {message}")

if __name__ == "__main__":
    start_server()