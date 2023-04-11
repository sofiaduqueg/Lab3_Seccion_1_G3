import socket, os, hashlib, datetime, sys

num_conex = 3
buffSize = 64000

host = '192.168.189.135'
port = 17000

separador = '||'

sockets = []

now = datetime.datetime.now()
logName = './Log/'+str(now.year)+"-"+str(now.month)+"-"+str(now.day)+"-("+str(now.hour)+"-"+str(now.minute)+"-"+str(now.second)+")-log.txt"

os.makedirs(os.path.dirname(logName), exist_ok=True)
log = open(logName,'wb')

# Crea el socket para establecer comunicación con el servidor
socketInicial = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
socketInicial.connect((host,port))
while True:
    bytes_r = socketInicial.recv(buffSize)
    if bytes_r.decode('utf-8') != "OK":
        # Imprime el mensaje desde el servidor con los archivos que se pueden descargar
        print(bytes_r.decode('utf-8'))
        resp = str(input())
        nomb_Archivo, num_conex_str = resp.split(",")
        num_conex = int(num_conex_str)
        # Responde al servidor con el archivo y el numero de conexiones que quiere generar
        socketInicial.send(str(resp).encode('utf-8'))
    else:
        break 
socketInicial.close()


# Conexión de cada uno de los clientes
for i in range(0,num_conex):
    sys.stdout.write("\r"+"Conectando Cliente"+str(i+1)+" al servidor")
    sockets.append(socket.socket(socket.AF_INET,socket.SOCK_STREAM))
    sockets[i].connect((host,port))
    sys.stdout.flush()
    sys.stdout.write("\r"+str(i+1)+" Clientes conectados al servidor ")
sys.stdout.write("\n")

# Envío de mensaje de confirmación
i=0
for s in sockets:
    s.send(str(s).encode('utf-8'))
i=1

for s in sockets:
    hashArchivo = ''
    c = True
    archivo = b''
    nombre = './ArchivosRecibidos/Cliente'+str(i)+'-Prueba-'+str(num_conex)+'.txt'
    os.makedirs(os.path.dirname(nombre), exist_ok=True)
    f = open(nombre, 'wb')
    t1 = datetime.datetime.now()
    t2 = t1
    while True:
        try:
            # Recibe los bytes que envía el servidor
            bytes_r = s.recv(buffSize)
            t2=datetime.datetime.now()
            if not bytes_r:
                t2=datetime.datetime.now()
                break
            else:
                # Extrae el Hash del mensaje si es necesario y agrega los bytes recibidos en el archivo
                if bytes_r.decode('utf-8').find(separador)==-1:
                    sys.stdout.flush()
                    sys.stdout.write("\r"+"Recepción del Cliente"+str(i)+" "+str(s)+" --------- Bytes recibidos: "+str(round(len(archivo)/1000000,2))+'MB')
                    archivo = archivo + bytes_r
                    f.write(bytes_r)
                else:
                    hashArchivo, _ = bytes_r.decode('utf-8').split(separador)
                    archivo = archivo + _.encode('utf-8')
                    f.write(_.encode('utf-8'))
        except:
            break

    f.close()
    logA = 'Cliente'+str(i)+'-'+str(s)+'\n'
    logA = logA +' Bytes recibidos '+str(len(archivo)/1000000)+'MB \n'
    logA = logA +' Hash recibido '+str(hashArchivo)+'\n'
    logA = logA +' Hash archivo '+str(hashlib.sha256(archivo).hexdigest())+'\n'
    logA = logA +' Tiempo de envío: '+str(t2-t1)+'\n'
    log.write(logA.encode('utf-8'))
    log.write('----------------------\n'.encode('utf-8'))
    sys.stdout.flush()
    sys.stdout.write("\r"+"Recepción del Cliente"+str(i)+" "+str(s)+" --------- Bytes recibidos: "+str(round(len(archivo)/1000000,2))+'MB'+" Conexión Cerrada \n")
    s.close()
     
            
    i=i+1
    
log.close()