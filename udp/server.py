import socket
import threading
import queue
import os
import logging
host = 'localhost'
port = 8000


if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = logging.FileHandler('logs/app.log')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)


messages = queue.Queue()
clients = []
files_info = queue.Queue()

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((host, port))


def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except:
            pass


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            print(message.decode())
            if addr not in clients:
                if (len(clients) >= 25):
                    logger.critical(
                        f"El servidor llego a su limite de usuarios {addr}")
                    server.sendto(
                        "El servidor llego a su limite de usuarios".encode(), addr)
                    break
                else:
                    logger.critical(
                        f"cliente añadido {addr}")
                    clients.append(addr)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP_TAG:"):
                        name = message.decode()[
                            message.decode().index(":")+1:]
                        server.sendto(f"{name} joined!".encode(), client)
                        logger.critical(
                            f"{name} se unio con la direccion {addr}")
                    else:
                        name, archivo, tam, num = message.decode().split(":")
                        files_info.put((name, archivo, tam, num))
                        logger.critical(
                            f"archivo {archivo} pedido por {name} con un tamaño de {tam} para el numero de usuarios {num}")
                        server.sendto(
                            f"archivo {archivo} pedido por {name} con un tamaño de {tam} para el numero de usuarios {num}".encode(), client)
                except:
                    print("error")
                    clients.remove(client)


def send_file():
    while True:
        while not files_info.empty():
            try:
                name, archivo, tam, num = files_info.get()
                file_size = os.path.getsize(archivo)
                if int(num) >= len(clients):
                    for client in clients:
                        server.sendto(
                            f"Se comenzaara con el envio de {archivo} solicitado por {name}".encode(), client)
                    logger.critical(
                        f"Se comenzaara con el envio de {archivo} solicitado por {name}")
                    with open(archivo, 'rb') as file:
                        sent_bytes = 0
                        while sent_bytes < file_size:
                            data = file.read(int(tam))
                            if not data:
                                break
                            for client in clients:
                                server.sendto(data, client)
                            sent_bytes += len(data)
                            logger.critical(
                                f"bytes {sent_bytes} del archivo {archivo} solicitado por {name} enviados, con chunks de tamaño {tam}")
            except Exception as e:
                print(str(e))


t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)
t3 = threading.Thread(target=send_file)

t1.start()
t2.start()
t3.start()
