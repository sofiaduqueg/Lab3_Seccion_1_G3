import socket
import threading
import random

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = int(input("puerto: "))
client.bind(("localhost", port))
name = input("Nickename: ")


def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode())
        except:
            pass


t = threading.Thread(target=receive)
t.start()

client.sendto(f"SIGNUP_TAG:{name}".encode(), ("localhost", 8000))

host = 'localhost'
port = 8000

while True:
    archivo = input("nombre del archivo: ")
    tam = input("tamaño de los chunks: ")
    num = input("numero de clientes: ")
    if tam == "-1":
        exit()
    else:
        client.sendto(f"{name}:{archivo}:{tam}:{num}".encode(), (host, port))
