import socket
import threading
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_client(client_socket, client_address):
    ip, port = client_address
    logging.info(f"{ip}:{port} подключился")

    try:
        while True:
            # Установим таймаут на чтение данных
            client_socket.settimeout(10)
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8').strip()
            logging.info(f"{ip}:{port} > {message}")
    except socket.timeout:
        logging.warning(f"{ip}:{port} - таймаут соединения")
    except ConnectionResetError:
        logging.warning(f"{ip}:{port} - соединение разорвано")
    except Exception as e:
        logging.error(f"{ip}:{port} - ошибка: {e}")
    finally:
        client_socket.close()
        logging.info(f"{ip}:{port} отключился")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(5)
    logging.info("Сервер запущен и слушает порт 80...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        logging.info("Сервер остановлен.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()