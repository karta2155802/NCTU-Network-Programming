import socket
import sys
import _thread
import sqlite3
from sqlite3 import Error


def sql_insert(msg_in, conn, c):
	try:
		msg_split = msg_in.split()
		reply=c.execute('insert into USERS ("Username", "Email", "Password") values (?,?,?)', (msg_split[1], msg_split[2], msg_split[3]))
		conn.commit()
		print('Insertion success')
	except Error:
		print('Username is already used')
		msg_out = 'Username is already used.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

def new_client(clientsocket, addr):
	conn = sqlite3.connect('Database.db')
	c = conn.cursor()
	print('Sql Connecttion Succeed')

	msg_out = 'Welcoome to the BBS server\r\n'
	clientsocket.send(msg_out.encode('utf-8'))
	clientsocket.recv(1024)
	#msg_out = '% '
	#clientsocket.send(msg_out.encode('utf-8'))
	msg_in = 'initial'
	while True:
		if msg_in != '':
			msg_out = '% '
			clientsocket.send(msg_out.encode('utf-8'))
		msg_in = clientsocket.recv(1024).decode('utf-8')
		print(msg_in)
		msg_in = msg_in.replace('\r','').replace('\n','')			
		
		#msg_list = msg_in.split();	
		try:
			string_processing(msg_in, conn, c)
		except:
			continue
		#msg_out = '% '
		#clientsocket.send(msg_out.encode('utf-8'))
		


def string_processing(msg_in, conn, c):
	msg_split = msg_in.split()
	if msg_split[0] == "register":
		if len(msg_split) != 4:
			msg_out = 'Usage: regoster <username> <email> <password>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		else:
			print('Inserting...')
			sql_insert(msg_in, conn, c)


	#elif str[0] == "login":
	#	if len(str) != 3:
	#		msg_out = 'Usage: login <username> <password>'
	#		clientsocket.send(msg_out.encode('utf-8'))
		

	#elif str[0] == 'logout':

	#elif str[0] == 'whoami':

	#elif str[0] == 'exit':


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname();
port = 10000
serversocket.bind((host, port))
serversocket.listen(11)
print("Waiting for connection...")

while True:
	clientsocket, addr = serversocket.accept();
	print("New Connection: %s" %str(addr))
	_thread.start_new_thread(new_client, (clientsocket, addr))