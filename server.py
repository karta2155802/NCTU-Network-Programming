import socket
import sys
import _thread

def new_client(clientsocket, addr):
	msg_out = 'Welcoome to the BBS server\r\n'
	clientsocket.send(msg_out.encode('utf-8'))
	msg_in = clientsocket.recv(1024)
	while True:
		msg_out = '%'
		clientsocket.send(msg_out.encode('utf-8'))
		msg_in = clientsocket.recv(1024)
		print(msg_in.decode('utf-8'))


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname();
port = 10000
serversocket.bind((host, port))
serversocket.listen(11)
print("Waiting for connection")

while True:
	clientsocket, addr = serversocket.accept();
	print("New Connection: %s" %str(addr))
	_thread.start_new_thread(new_client, (clientsocket, addr))