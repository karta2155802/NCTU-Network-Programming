import socket
import sys
import _thread
import sqlite3
from sqlite3 import Error



def sql_connection():
	try:
		con = sqlite3.connect('Database.db')
		print('sql connect success')
		return con
	except Error:
		print(Error)

def sql_insert(str):
	try:
		cursorObj.execute("insert into  USERS (Username, Email, Password) values (?,?,?)", (str[1], str[2], str[3]))
	except Error:
		print(Error)
		msg_out = 'Username is already used.'
		clientsocket.send(msg_out.encode('utf-8'))

def new_client(clientsocket, addr):
	msg_out = 'Welcoome to the BBS server\r\n'
	
	clientsocket.recv(1024)
	msg_in = 'initial'
	while True:
		if msg_in != '': 
			msg_out = '% '
			clientsocket.send(msg_out.encode('utf-8'))
		msg_in = clientsocket.recv(1024).decode('utf-8')
		msg_in = msg_in.replace('\r','').replace('\n','')
		print(msg_in)
		msg_list  = msg_in.split();
		string_processing(msg_list)


def string_processing(str):
	if str[0] == 'register':
		if len(str) != 4:
			msg_out = 'Usage: regoster <username> <email> <password>'
			clientsocket.send(msg_out.encode('utf-8'))
		else:
			print('Inserting')
			sql_insert(str)
			print('Finish insert')


	elif str[0] == 'login':
		if len(str) != 3:
			msg_out = 'Usage: login <username> <password>'
			clientsocket.send(msg_out.encode('utf-8'))
		else:

	#elif str[0] == 'logout':

	#elif str[0] == 'whoami':

	#elif str[0] == 'exit':


con = sql_connection()
cursorObj = con.cursor()

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