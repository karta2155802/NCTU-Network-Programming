import socket
import sys
import thread

def new_client(clientsocket, addr):
	msg_out = 'Welcoome to the BBS server'
	clientsocket.send(msg_out.encode('utf-8'))
	while True:
		msg_out = '%'
		clientsocket.send(msg_out.encode('utf-8'))
		msg_in = s.recv(1024)
		print(msg_in.decode('utf-8'))


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname();
port = 10000
serversocket.bind((host, port))
serversocket.listen(11)

while True:
	clientsocket, addr = serversocket.accept();
	print("New Connection: %s" %str(addr))
	thread.start_new_thread(new_client, (clientsocket, addr))

	
	
	
	msg_in = s.recv(1024)
