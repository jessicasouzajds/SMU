import socket

s = socket.socket()
s.connect(('191.36.14.78',5556))   # se conecta com o servidor através de seu IP

uri = str("rtsp://admin:admin@191.36.14.72:554/cam/realmonitor?channel=1&subtype=0")
s.send(uri.encode())

print ("Recebeu do server:",s.recv(1024).decode())

s.close()


