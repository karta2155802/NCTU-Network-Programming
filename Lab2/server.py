import socket
import sys
import _thread
import sqlite3
import time
from sqlite3 import Error

def sql_update_post_title(conn, c, uid, post_id, update_data):
	sql_return_fetch = c.execute('select Author_id from POST where ID = ?', (post_id,)).fetchone()	
	if sql_return_fetch == None:
		msg_out = 'Post is not exist.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	elif sql_return_fetch[0] != uid:
		msg_out = 'Not the post owner.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	else:
		c.execute('update POST set Title = ? where ID = ?', (update_data, post_id))
		conn.commit()
		print('Update post title successfully')
		msg_out = 'Update successfully.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

def sql_update_post_content(conn, c, uid, post_id, update_data):
	sql_return_fetch = c.execute('select Author_id from POST where ID = ?', (post_id,)).fetchone()
	if sql_return_fetch == None:
		msg_out = 'Post is not exist.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	elif sql_return_fetch[0] != uid:
		msg_out = 'Not the post owner.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	else:
		c.execute('update POST set Content = ? where ID = ?', (updata_date, post_id))
		conn.commit()
		print('Update post content successfully')
		msg_out = 'Update successfully.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

def sql_comment(conn, c , uid, post_id, comment):
	sql_return_fetch = c.execute('select ID from POST where ID = ?', (post_id,)).fetchone()
	if sql_return_fetch == None:
		msg_out = 'Post is not exist.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	else:
		c.execute('insert into COMMENT ("Writer_id", "Comment", "Post_id") values (?,?,?)', (uid, comment, post_id))
		conn.commit()
		print('Comment successfully')
		msg_out = 'Comment successfully.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

def sql_delete_post(conn, c, uid, post_id):
	sql_return_fetch = c.execute('select Author_id from POST where ID = ?', (post_id,)).fetchone()
	if sql_return_fetch == None:
		msg_out = 'Post is not exist.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	elif sql_return_fetch[0] != uid:
		msg_out = 'Not the post owner.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	else:
		c.execute('delete from POST where ID = ?', (post_id,))
		print('Delete successfully')
		msg_out = 'Delete successfully\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

def sql_read_post(c, post_id):
	sql_return_fetch = c.execute('select USERS.Username, POST.Title, POST.Date, POST.Content from POST inner join USERS on POST.Author_id = USERS.UID where POST.ID = ?', (post_id,)).fetchone()
	if sql_return_fetch == None:
		msg_out = 'Post is not exist.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	else:
		msg_out = '\r\n    {:<10}:{}\r\n'.format('Author', sql_return_fetch[0])
		clientsocket.send(msg_out.encode('utf-8'))
		msg_out = '    {:<10}:{}\r\n'.format('Title', sql_return_fetch[1])
		clientsocket.send(msg_out.encode('utf-8'))
		msg_out = '    {:<10}:{}\r\n'.format('Date', sql_return_fetch[2])
		clientsocket.send(msg_out.encode('utf-8'))
		msg_out = '    --\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

		content = sql_return_fetch[3].split('<br>')
		for i in content:
			msg_out = '    {}\r\n'.format(i)
			clientsocket.send(msg_out.encode('utf-8'))

		msg_out = '    --\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
		sql_return_comment = c.execute('select USERS.Username, COMMENT.Comment from COMMENT inner join USERS on COMMENT.Writer_id = USERS.UID where Post_id = ?', (post_id))
		for row in sql_return_comment:
			msg_out = '    {}: {}\r\n'.format(row[0], row[1])
			clientsocket.send(msg_out.encode('utf-8'))
		msg_out = '\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
		print('Read post successfully')

def sql_list_post(c, board_name, keyword):
	sql_return_fetch = c.execute('select BOARD.ID from BOARD where BOARD.Name = ?', (board_name,)).fetchone()
	if sql_return_fetch == None:
		msg_out = 'Board is not exist.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	else:
		board_id = sql_return_fetch[0]
		print('board_id =', board_id)
		sql_return_post = c.execute('select POST.ID, POST.Title, USERS.Username, POST.Date from POST inner join USERS on POST.Author_id = USERS.UID where Board_id = ? and POST.Title like ?', (board_id, keyword))
		msg_out = '\r\n    {:<7} {:<20} {:<12} {:<9}\r\n'.format('ID', 'Title', 'Author', 'Date')
		clientsocket.send(msg_out.encode('utf-8'))
		for row in sql_return_post:
			msg_out = '    {:<7} {:<20} {:<12} {:<9}\r\n'.format(row[0], row[1], row[2], row[3])
			clientsocket.send(msg_out.encode('utf-8'))
		msg_out = '\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
		print('List post successfully')

def sql_list_board(c, keyword):
	sql_return = c.execute('select BOARD.ID, BOARD.Name, USERS.Username from BOARD inner join USERS on BOARD.Moderator_id = USERS.UID where BOARD.Name like ?', (keyword,))
	msg_out = '\r\n    {:<7} {:^20} {:^20}\r\n'.format('Index', 'Name', 'Moderator')
	clientsocket.send(msg_out.encode('utf-8'))
	for row in sql_return:
		msg_out = '    {:<7} {:^20} {:^20}\r\n'.format(row[0], row[1], row[2])
		clientsocket.send(msg_out.encode('utf-8'))
	msg_out = '\r\n'
	clientsocket.send(msg_out.encode('utf-8'))
	print('List board successfully')

def sql_create_post(conn, c, uid, data):
	sql_return = c.execute('select * from BOARD where Name = ?', (data[0],)).fetchone()
	if(sql_return == None):
		print('Board is not exist')
		msg_out = 'Board is not exist.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	else:
		board_id = sql_return[0]
		nowtime =  time.strftime('%m/%d', time.localtime())
		print('nowtime =', nowtime)
		c.execute('insert into POST ("Title", "Author_id", "Date", "Content", "Board_id") values (?,?,?,?,?)', (data[1], uid, nowtime, data[2], board_id))
		conn.commit()
		print('Create post successfully')
		msg_out = 'Create post successfully.\r\n'
		clientsocket.send(msg_out.encode('utf-8'))

def sql_create_board(msg_list, conn, c, uid):
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
	sql_return = c.execute('select * from USERS where UID = ?', (uid,)).fetchone()
	msg_out = sql_return[1] + '\r\n'
	clientsocket.send(msg_out.encode('utf-8'))

def sql_logout(msg_list, c, uid):
	sql_return = c.execute('select * from USERS where UID = ?', (uid,)).fetchone()
	msg_out = 'Bye, ' + sql_return[1] + '.\r\n'
	clientsocket.send(msg_out.encode('utf-8'))
	uid = -1
	print(sql_return[1],'has logout')
	return uid

def sql_login(msg_list, c, uid):
	sql_return = c.execute('select * from USERS where Username = ?', (msg_list[1],)).fetchone()
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

def string_processing(msg_in, conn, c, uid):
	hashtag = '##'
	msg_list = msg_in.split();
	print('uid =',uid)
	if msg_list[0] == 'register':
		if len(msg_list) != 4:
			msg_out = 'Usage: regoster <username> <email> <password>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		else:
			print('Inserting...')
			sql_register(msg_list, conn, c)
	elif msg_list[0] == 'login':
		if uid != -1:
			msg_out = 'Please logout first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) != 3:
			msg_out = 'Usage: login <username> <password>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))		
		elif len(msg_list) == 3 and uid == -1:
			print('Logging...')
			uid = sql_login(msg_list, c, uid)
	elif msg_list[0] == 'logout':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		if len(msg_list) != 1:
			msg_out = 'Usage: logout\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		else:
			print('Logout...')
			uid = sql_logout(msg_list, c, uid)
	elif msg_list[0] == 'whoami':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))	
		elif len(msg_list) != 1:
			msg_out = 'Usage: whoami\r\n'
			clientsocket.send(msg_out.encode('utf-8'))			
		else:
			print('whoami...')
			sql_whoami(c,uid)
	elif msg_list[0] == 'create-board':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) != 2:
			msg_out = 'Usage: create-board <name>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))		
		else:
			print('creating board...')
			sql_create_board(msg_list, conn, c, uid)
	elif msg_list[0] == 'create-post':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) > 5 and msg_list[2] == '--title' and '--content' in msg_in:
			board_name = msg_list[1]
			print('board_name =', board_name)
			content_position = msg_list.index('--content')
			title = ' '.join(msg_list[3:content_position])			
			print('title =', title)
			content = ' '.join(msg_list[content_position+1:len(msg_list)])
			print('content =', content)
			if title == '' or content == '':
				msg_out = 'Usage: create-post <board-name> --title <title> --content <content>\r\n'
				clientsocket.send(msg_out.encode('utf-8'))
			else:
				data = [board_name, title, content]
				print('creating post...')
				sql_create_post(conn, c, uid, data)
		else:
			msg_out = 'Usage: create-post <board-name> --title <title> --content <content>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
	elif msg_list[0] == 'list-board':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) == 1:
			keyword = '%%';
			print('search without hashtag')	
			sql_list_board(c, keyword)			
		elif len(msg_list) == 2 and hashtag in msg_list[1]:
			keyword = '%' + msg_list[1].replace('##', '', 1) + '%'
			print('keyword =', keyword)
			sql_list_board(c, keyword)				
		else:
			msg_out = 'Usage: list-board ##<key>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
	elif msg_list[0] == 'list-post':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) == 2:
			board_name = msg_list[1]
			keyword = '%%'
			print('search without hashtag')
			sql_list_post(c, board_name, keyword)
		elif len(msg_list) >2 and hashtag in msg_list[2]:
			board_name = msg_list[1]
			msg_list[2] = msg_list[2].replace('##','',1)
			keyword = '%' + ' '.join(msg_list[2:len(msg_list)]) + '%'
			print('keyword =', keyword)
			sql_list_post(c, board_name, keyword)
		else:
			msg_out = 'Usage: list-post <board-name> ##<key>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
	elif msg_list[0] == 'read':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) == 2:
			post_id = msg_list[1]
			sql_read_post(c, post_id)
		else:
			msg_out = 'Usage: read <post-id> \r\n'
			clientsocket.send(msg_out.encode('utf-8'))
	elif msg_list[0] == 'delete-post':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) == 2:
			post_id = msg_list[1]
			print('Deleting post...')
			sql_delete_post(conn, c, uid, post_id)
		else:
			msg_out = 'Usage: delete-post <post-id> \r\n'
			clientsocket.send(msg_out.encode('utf-8'))
	elif msg_list[0] == 'update-post':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) > 3 and msg_list[2] == '--title':
			post_id = msg_list[1]
			update_data = ''.join(msg_list[3:len(msg_list)])
			print('Updating post title =', update_data)
			sql_update_post_title(conn, c, uid, post_id, update_data)
		elif len(msg_list) > 3 and msg_list[2] == '--content':
			post_id = msg_list[1]
			update_data = ''.join(msg_list[3:len(msg_list)])
			print('Updating post content', update_data)
			sql_update_post_content(conn, c, uid, post_id, update_data)
		else:
			msg_out = 'Usage: update-post <post-id> --title/content <new>\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
	elif msg_list[0] == 'comment':
		if uid == -1:
			msg_out = 'Please login first.\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
		elif len(msg_list) > 2:
			post_id = msg_list[1]
			comment = ''.join(msg_list[2:len(msg_list)])
			print('comment =', comment)
			sql_comment(conn, c, uid, post_id, comment)
		else:
			msg_out = 'Usage: comment <post-id> <comment> \r\n'
			clientsocket.send(msg_out.encode('utf-8'))
	else:
		msg_out = 'Command not found\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
	print('')
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
	uid = -1
	count = 0
	while True:		
		msg_in = clientsocket.recv(1024).decode('utf-8')
		if msg_in == '\r\n':
			msg_out = '% '
			clientsocket.send(msg_out.encode('utf-8'))
			continue
		elif msg_in == '':
			count += 1
			if count == 3:
				clientsocket.close()
				break		
		msg_in = msg_in.replace('\r','').replace('\n','')			
		print('msg_in = ',msg_in)
		
		if msg_in == 'exit':
			clientsocket.close()
			break
		else:
			#try:
			uid = string_processing(msg_in, conn, c, uid)
			#except:
				#print('string processing error')
				#continue
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