import socket, os, hashlib, sys, datetime
from tabulate import tabulate

buffSize = 64000

num_conex = 1 # Se establece 1 por defecto
nomb_Archivo = '' # Se establece vacio pues lo define el Cliente
separador = '||' # Separador para diferenciar el hash del contenido 

host = '0.0.0.0'
port = 17000

sockets = [] # Arreglo que contiene la información de los sockets del Cliente

# Se crea el Log
now = datetime.datetime.now()
logName = './Log/'+str(now.year)+"-"+str(now.month)+"-"+str(now.day)+"-("+str(now.hour)+"-"+str(now.minute)+"-"+str(now.second)+")-log.txt"
os.makedirs(os.path.dirname(logName), exist_ok=True)
log = open(logName,'wt')

# Se crea el socket del servidor 
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,buffSize)
s.bind((host, port))

# Mensaje pidiendo el input del archivo y número de conexiones al Cliente
mensaje =           "----------------------------------------------------\n"
mensaje = mensaje + "------------------- Servidor TCP -------------------\n"
mensaje = mensaje + "Indique el archivo a recibir y el número de clientes\n"
mensaje = mensaje + "separado por coma y sin espacio (Ej 1.txt,25)\n"

archivos = os.listdir()
table = [["Archivo", "Tamaño"],]
for arch in archivos:
    tam = str(round(os.path.getsize(arch)/1000000,2))+"MB"
    table.append([arch, tam])
mensaje = mensaje + tabulate(table,headers='firstrow') + "\n"
mensaje = mensaje + "----------------------------------------------------\n"

# Primera conexión con el cliente, envía el mensaje y espera la respuesta del cliente
s.listen(1)
ss, _ = s.accept()

while True:
    ss.sendall(mensaje.encode('utf-8'))
    rec = ss.recv(buffSize)
    m = rec.decode('utf-8')
    if m.find(",")!=-1:
        nomb_Archivo, num_conex_str = m.split(",")
        num_conex = int(num_conex_str)
        ss.sendall('OK'.encode('utf-8'))
        ss.close()
        break


log.write("Archivo enviado "+nomb_Archivo+"\n")
archivo = open(nomb_Archivo, 'rb')
log.write("Tamaño del archivo "+ str(round(os.path.getsize(nomb_Archivo)/1000000,2))+"MB \n")

hashArchivo = str(hashlib.sha256(archivo.read()).hexdigest())

# Se esperan y aceptan las conexiones que definió el Cliente 
s.listen(num_conex)
for i in range(0,num_conex):
    sys.stdout.write("\r"+"Esperando la conexión del Cliente"+str(i+1)+" al servidor")
    ss, _ = s.accept()
    sys.stdout.flush()
    sockets.append(ss)
    sys.stdout.write("\r"+str(i+1)+" Clientes conectados al servidor                        ")
sys.stdout.write("\n")

# Espera el mensaje de confirmación de los clientes para enviar el archivo
i=1
for soc in sockets:
    rec = soc.recv(buffSize)
    print("Cliente"+str(i)+"-"+ rec.decode('utf-8')+ " - OK")
    i=i+1

for i in range(0,num_conex):
    # Primero envía el hash
    sys.stdout.flush()
    mens = hashArchivo+separador
    sockets[i].sendall(mens.encode('utf-8'))
    f = open(nomb_Archivo,'rb')
    c= True
    env = 0 
    t1 = datetime.datetime.now()
    while c:
        try:
        #   Envía el contenido del archivo
            bytes_read = f.read(buffSize)
            env = env + len(bytes_read)
            if not bytes_read:
                # Termina el while cuando no se transmita más del archivo
                c= False
            else:
                # Muestra en consola el progreso para el Cliente i y envía el paquete
                sys.stdout.flush()
                sys.stdout.write("\r"+"Transmitiendo al Cliente"+str(i+1)+" --------- Bytes enviados: "+str(round(env/1000000,2))+'MB')
                sys.stdout.flush()
                sockets[i].sendall(bytes_read)
        except:
            break
    t2 = datetime.datetime.now()
    sockets[i].close()
    sys.stdout.flush()
    sys.stdout.write("\r"+"Transmitiendo al Cliente"+str(i+1)+" --------- Bytes enviados: "+str(round(env/1000000,2))+'MB - Conexión cerrada\n')
    # Escribe en el log el cliente, los Bytes que se enviaron y el tiempo de transferencia
    log.write("Cliente"+str(i)+"\n")
    log.write("Bytes enviados :"+str(round(env/1000000,2))+"MB\n")
    log.write("Tiempo de transferencia :"+str(t2-t1)+"\n")
    log.write("---------------\n")

s.close()