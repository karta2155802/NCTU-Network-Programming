import socket
import sys
import _thread
import sqlite3
from sqlite3 import Error

def sql_creat_board(msg_list, conn, c, uid):
	try:
		c.execute('insert into BOARD ("Name", "Moderator_id") values (?,?)', (msg_list[1], uid))
		conn.commit()
		print('Create board successfully')
		msg_out = 'Create board successfully.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	except Error:
		print('Board is already exist')
		msg_out = 'Board is already exist.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

def sql_whoami(c, uid):
	sql_return = c.execute('select * from USERS where UID = ?',(uid,))
	sql_return = sql_return.fetchone()
	msg_out = sql_return[1] + '\r\n'
	clientsocket.send(msg_out.encode('utf-8'))

def sql_logout(msg_list, c, uid):
	if uid != -1:
		sql_return = c.execute('select * from USERS where UID = ?',(uid,))
		sql_return = sql_return.fetchone()
		msg_out = 'Bye, ' + sql_return[1] + '.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
		uid = -1
		print(sql_return[1],'has logout')
	else:
		msg_out = 'Please login first\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	return uid

def sql_login(msg_list, c, uid):
	sql_return = c.execute('select * from USERS where Username = ?',(msg_list[1],))
	sql_return = sql_return.fetchone()
	if sql_return != None and sql_return[3] == msg_list[2]:
		uid = sql_return[0]
		print(msg_list[1],'has login')
		msg_out = 'Welcome, ' + msg_list[1] +'.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	else:
		msg_out = 'Login failed.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	return uid

def sql_register(msg_list, conn, c):
	try:
		c.execute('insert into USERS ("Username", "Email", "Password") values (?,?,?)', (msg_list[1], msg_list[2], msg_list[3]))
		conn.commit()
		print('Register successfully')
		msg_out = 'Register successfully.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	except Error:
		print('Username is already used')
		msg_out = 'Username is already used.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

def string_processing(msg_list, conn, c, uid):
	print(uid)
	if msg_list[0] == 'register':
		if len(msg_list) != 4:
			msg_out = 'Usage: regoster <username> <email> <password>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		else:
			print('Inserting...')
			sql_register(msg_list, conn, c)
	elif msg_list[0] == 'login':
		if len(msg_list) != 3:
			msg_out = 'Usage: login <username> <password>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) == 3 and uid != -1:
			msg_out = 'Please logout first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) == 3 and uid == -1:
			print('Logging...')
			uid = sql_login(msg_list, c, uid)
	elif msg_list[0] == 'logout':
		if len(msg_list) != 1:
			msg_out = 'Usage: logout\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		else:
			print('Logout...')
			uid = sql_logout(msg_list, c, uid)
	elif msg_list[0] == 'whoami':
		if len(msg_list) != 1:
			msg_out = 'Usage: whoami\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))		
		else:
			print('whoami...')
			sql_whoami(c,uid)
	elif msg_list[0] == 'create-board':
		if len(msg_list) != 2:
			msg_out = 'Usage: create-board <name>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		else:
			print('creating board...')
			sql_create_board(msg_list, conn, c, uid)
	return uid

def new_client(clientsocket, addr):
	conn = sqlite3.connect('Database.db')
	c = conn.cursor()
	print('Sql Connecttion Succeed')
	msg_out = '********************************\r\n'
	clientsocket.send(msg_out.encode('utf-8'))
	msg_out = '** Welcoome to the BBS server **\r\n'
	clientsocket.send(msg_out.encode('utf-8'))
	msg_out = '********************************\r\n'
	clientsocket.send(msg_out.encode('utf-8'))
	clientsocket.recv(1024)

	msg_out = '% '
	clientsocket.send(msg_out.encode('utf-8'))
	uid=-1
	while True:		
		msg_in = clientsocket.recv(1024).decode('utf-8')		
		msg_in = msg_in.replace('\r','').replace('\n','')			
		print('msg_in = ',msg_in)
		msg_list = msg_in.split();
		
		if msg_in == 'exit':
			clientsocket.close()
			break
		else:
			try:
				uid = string_processing(msg_list, conn, c, uid)
			except:
				#print('string processing error')
				continue
		msg_out = '% '
		clientsocket.send(msg_out.encode('utf-8'))

		

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname();
port = 10000
serversocket.bind((host, port))
serversocket.listen(20)
print('Waiting for connection...')

while True:
	clientsocket, addr = serversocket.accept();
	print('New Connection: %s' %str(addr))
	_thread.start_new_thread(new_client, (clientsocket, addr))