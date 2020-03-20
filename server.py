import socket
import sys

serversocket = socket.socket(socket.AFINET, sockket.SOCK_STEAM)
host = socket.gethostname();
port = 10000
serversocket.bind((host, port))
serversocket.listen(11)

while Ture:
	clientsocket, addr = serversocket.accept();
	print("New Connection: %s" %str(addr))

	msg = 'Welcoome to the BBS server'
	clientsocket.send(msg.encode('utf-8'))
	clientsocket.close()
