import socket
import sys
import _thread
import sqlite3
import time


def new_client(clientsocket, addr):
	msg_suc = ""
#------------------------------------------------------sqlite3 function
	def sql_retr_mail(c, uid, mail_id):
		sql_return = c.execute('select * from MAIL inner join USERS on MAIL.Receiver = USERS.Username where UID = ?', (uid,)).fetchall()
		if len(sql_return) < int(mail_id):
			msg_suc = 'No such mail.\r\n'
		else:
			bucket_name = c.execute('select Bucket_name from USERS where UID = ?', (uid,)).fetchone()[0]
			msg_out1 = '\r\n    {:<10}:{}\r\n'.format('Subject', sql_return[int(mail_id)-1][1])
			msg_out2 = '    {:<10}:{}\r\n'.format('From', sql_return[int(mail_id)-1][2])
			msg_out3 = '    {:<10}:{}'.format('Date', sql_return[int(mail_id)-1][4])
			msg_out = msg_out1 + msg_out2 + msg_out3 + '###' + str(sql_return[int(mail_id)-1][0]) + '###' + bucket_name
			clientsocket.send(msg_out.encode('utf-8'))			
			print('Retr mail successfully')
			msg_suc = ""
		return msg_suc

	def sql_list_mail(c,uid):
		sql_return = c.execute('select * from MAIL inner join USERS on MAIL.Receiver = USERS.Username where UID = ?', (uid,)).fetchall()
		msg_out = '\r\n    {:<7} {:<20} {:<12} {:<9}\r\n'.format('ID', 'Subject', 'From', 'Date')
		clientsocket.send(msg_out.encode('utf-8'))
		for i in range(len(sql_return)):
			msg_out = '    {:<7} {:<20} {:<12} {:<9}\r\n'.format(i+1, sql_return[i][1], sql_return[i][2], sql_return[i][4])
			clientsocket.send(msg_out.encode('utf-8'))
		msg_out = '\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
		print('List mail successfully')
		msg_suc = ""
		return msg_suc

	def sql_mail_to(conn, c, uid, data):
		sql_return = c.execute('select Bucket_name from USERS where Username = ?', (data[0],)).fetchone()
		if(sql_return == None):
			print('<username> does not exist.')
			msg_suc = '<username> does not exist.\r\n'
		else:
			target_bucket = sql_return[0]
			nowtime =  time.strftime('%m/%d', time.localtime())
			sender = c.execute('select Username from USERS where UID = ?', (uid,)).fetchone()[0]
			c.execute('insert into MAIL ("Subject", "Sender", "Receiver", "Date") values (?,?,?,?)', (data[1], sender, data[0], nowtime))
			conn.commit()
			sql_return = c.execute('select * from MAIL where Subject = ?', (data[1],)).fetchall()
			print('Sent successfully')
			msg_suc = 'Sent successfully.\r\n' + '###' + str(sql_return[-1][0]) + '###' + target_bucket
		return msg_suc

	def sql_update_post_title(conn, c, uid, post_id, update_data):
		sql_return = c.execute('select Author_id from POST where ID = ?', (post_id,)).fetchone()	
		if sql_return == None:
			msg_suc = 'Post is not exist.\r\n'
		elif sql_return[0] != uid:
			msg_suc = 'Not the post owner.\r\n'
		else:
			c.execute('update POST set Title = ? where ID = ?', (update_data, post_id))
			conn.commit()
			print('Update post title successfully')
			msg_suc = 'Update successfully.\r\n'
		return msg_suc

	def sql_update_post_content(conn, c, uid, post_id, update_data):
		sql_return = c.execute('select Author_id from POST where ID = ?', (post_id,)).fetchone()
		if sql_return == None:
			msg_suc = 'Post is not exist.\r\n'
		elif sql_return[0] != uid:
			msg_suc = 'Not the post owner.\r\n'
		else:
			print('Update post content successfully')
			msg_suc = 'Update successfully.\r\n'
		return msg_suc

	def sql_comment(conn, c , uid, post_id, comment):
		sql_return = c.execute('select ID from POST where ID = ?', (post_id,)).fetchone()
		if sql_return == None:
			msg_suc = 'Post is not exist.\r\n'
		else:
			author_id = c.execute('select Author_id from POST where ID = ?', (post_id,)).fetchone()[0]
			bucket_name = c.execute('select Bucket_name from USERS where UID = ?', (author_id,)).fetchone()[0]
			commentter = c.execute('select Username from USERS where UID = ?', (uid,)).fetchone()[0]
			print('Comment successfully')
			msg_suc = 'Comment successfully.\r\n' + '###' + bucket_name + '###' + commentter
		return msg_suc

	def sql_delete_post(conn, c, uid, post_id):
		sql_return = c.execute('select Author_id from POST where ID = ?', (post_id,)).fetchone()
		if sql_return == None:
			msg_suc = 'Post is not exist.\r\n'
		elif sql_return[0] != uid:
			msg_suc = 'Not the post owner.\r\n'
		else:
			c.execute('delete from POST where ID = ?', (post_id,))
			c.execute('delete from COMMENT where Post_id = ?', (post_id,))
			conn.commit()
			print('Delete successfully')
			msg_suc = 'Delete successfully.\r\n'
		return msg_suc

	def sql_read_post(c, post_id):
		sql_return = c.execute('select USERS.Username, POST.Title, POST.Date from POST inner join USERS on POST.Author_id = USERS.UID where POST.ID = ?', (post_id,)).fetchone()
		if sql_return == None:
			msg_suc = 'Post is not exist.\r\n'
		else:
			bucket_name = c.execute('select Bucket_name from USERS where Username = ?', (sql_return[0],)).fetchone()[0]
			msg_out1 = '\r\n    {:<10}:{}\r\n'.format('Author', sql_return[0])
			msg_out2 = '    {:<10}:{}\r\n'.format('Title', sql_return[1])
			msg_out3 = '    {:<10}:{}'.format('Date', sql_return[2])
			msg_out = msg_out1 + msg_out2 + msg_out3 + '###' + bucket_name
			clientsocket.send(msg_out.encode('utf-8'))			
			print('Read post successfully')
			msg_suc = ""
		return msg_suc

	def sql_list_post(c, board_name, keyword):
		sql_return = c.execute('select BOARD.ID from BOARD where BOARD.Name = ?', (board_name,)).fetchone()
		if sql_return == None:
			msg_suc = 'Board is not exist.\r\n'
		else:
			board_id = sql_return[0]
			print('board_id =', board_id)
			c.execute('PRAGMA case_sensitive_like = 1')
			sql_return_post = c.execute('select POST.ID, POST.Title, USERS.Username, POST.Date from POST inner join USERS on POST.Author_id = USERS.UID where Board_id = ? and POST.Title like ?', (board_id, keyword))
			msg_out = '\r\n    {:<7} {:<20} {:<12} {:<9}\r\n'.format('ID', 'Title', 'Author', 'Date')
			clientsocket.send(msg_out.encode('utf-8'))
			for row in sql_return_post:
				msg_out = '    {:<7} {:<20} {:<12} {:<9}\r\n'.format(row[0], row[1], row[2], row[3])
				clientsocket.send(msg_out.encode('utf-8'))
			msg_out = '\r\n'
			clientsocket.send(msg_out.encode('utf-8'))
			print('List post successfully')
			msg_suc = ""
		return msg_suc

	def sql_list_board(c, keyword):
		c.execute('PRAGMA case_sensitive_like = 1')
		sql_return = c.execute('select BOARD.ID, BOARD.Name, USERS.Username from BOARD inner join USERS on BOARD.Moderator_id = USERS.UID where BOARD.Name like ?', (keyword,))
		msg_out = '\r\n    {:<7} {:^20} {:^20}\r\n'.format('Index', 'Name', 'Moderator')
		clientsocket.send(msg_out.encode('utf-8'))
		for row in sql_return:
			msg_out = '    {:<7} {:^20} {:^20}\r\n'.format(row[0], row[1], row[2])
			clientsocket.send(msg_out.encode('utf-8'))
		msg_out = '\r\n'
		clientsocket.send(msg_out.encode('utf-8'))
		print('List board successfully')
		msg_suc = ""
		return msg_suc

	def sql_create_post(conn, c, uid, data):
		sql_return = c.execute('select * from BOARD where Name = ?', (data[0],)).fetchone()
		if(sql_return == None):
			print('Board is not exist')
			msg_suc = 'Board is not exist.\r\n'
		else:
			board_id = sql_return[0]
			nowtime =  time.strftime('%m/%d', time.localtime())
			c.execute('insert into POST ("Title", "Author_id", "Date", "Board_id") values (?,?,?,?)', (data[1], uid, nowtime, board_id))
			conn.commit()
			sql_return = c.execute('select * from POST where Title = ?', (data[1],)).fetchall()
			print('Create post successfully')
			msg_suc = 'Create post successfully.\r\n' + '###' + str(sql_return[-1][0])
		return msg_suc

	def sql_create_board(msg_list, conn, c, uid):
		sql_return = c.execute('select * from BOARD where Name = ?', (msg_list[1],)).fetchall()
		if len(sql_return) == 0:
			c.execute('insert into BOARD ("Name", "Moderator_id") values (?,?)', (msg_list[1], uid))
			conn.commit()
			print('Create board successfully')
			msg_suc = 'Create board successfully.\r\n'
		else:
			print('Board is already exist')
			msg_suc = 'Board is already exist.\r\n'
		return msg_suc

	def sql_whoami(c, uid):
		sql_return = c.execute('select * from USERS where UID = ?', (uid,)).fetchone()
		msg_suc = sql_return[1] + '\r\n'
		return msg_suc

	def sql_logout(msg_list, c, uid):
		sql_return = c.execute('select * from USERS where UID = ?', (uid,)).fetchone()
		msg_suc = 'Bye, ' + sql_return[1] + '.\r\n'
		uid = -1
		print(sql_return[1],'has logout')
		return uid, msg_suc

	def sql_login(msg_list, c, uid):
		sql_return = c.execute('select * from USERS where Username = ?', (msg_list[1],)).fetchone()
		if sql_return != None and sql_return[3] == msg_list[2]:
			uid = sql_return[0]
			print(msg_list[1],'has login')
			msg_suc = 'Welcome, ' + msg_list[1] + '.\r\n' + '###' + sql_return[4]
		else:
			msg_suc = 'Login failed.\r\n'
		return uid, msg_suc

	def sql_register(msg_list, conn, c):
		sql_return = c.execute('select * from USERS where Username = ?', (msg_list[1],)).fetchall()
		if len(sql_return) == 0:
			bucket_name = '0516319-' + msg_list[1] + '-0516319'
			c.execute('insert into USERS ("Username", "Email", "Password", "Bucket_name") values (?,?,?,?)', (msg_list[1], msg_list[2], msg_list[3], bucket_name))
			conn.commit()
			print('Register successfully')
			msg_suc = 'Register successfully.\r\n'
		else:
			print('Username is already used')
			msg_suc = 'Username is already used.\r\n'
		return msg_suc

	def string_processing(msg_in, conn, c, uid):
		hashtag = '##'
		msg_list = msg_in.split();
		if msg_list[0] == 'register':
			if len(msg_list) != 4:
				msg_suc = 'Usage: register <username> <email> <password>\r\n'
			else:
				msg_suc = sql_register(msg_list, conn, c)
		elif msg_list[0] == 'login':
			if uid != -1:
				msg_suc = 'Please logout first.\r\n'
			elif len(msg_list) != 3:
				msg_suc = 'Usage: login <username> <password>\r\n'
			elif len(msg_list) == 3 and uid == -1:
				uid, msg_suc = sql_login(msg_list, c, uid)
		elif msg_list[0] == 'logout':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) != 1:
				msg_suc = 'Usage: logout\r\n'
			else:
				print('Logout...')
				uid, msg_suc = sql_logout(msg_list, c, uid)
		elif msg_list[0] == 'whoami':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) != 1:
				msg_suc = 'Usage: whoami\r\n'
			else:
				print('whoami...')
				msg_suc = sql_whoami(c,uid)
		elif msg_list[0] == 'create-board':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) != 2:
				msg_suc = 'Usage: create-board <name>\r\n'
			else:
				msg_suc = sql_create_board(msg_list, conn, c, uid)
		elif msg_list[0] == 'create-post':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) > 5 and msg_list[2] == '--title' and '--content' in msg_in:
				board_name = msg_list[1]
				print('board_name =', board_name)
				content_position = msg_list.index('--content')
				title = ' '.join(msg_list[3:content_position])			
				print('title =', title)
				content = ' '.join(msg_list[content_position+1:len(msg_list)])
				print('content =', content)
				if title == '' or content == '':
					msg_suc = 'Usage: create-post <board-name> --title <title> --content <content>\r\n'
				else:
					data = [board_name, title, content]
					msg_suc = sql_create_post(conn, c, uid, data)
			else:
				msg_suc = 'Usage: create-post <board-name> --title <title> --content <content>\r\n'
		elif msg_list[0] == 'list-board':
			if len(msg_list) == 1:
				keyword = '%%';
				print('search without hashtag')	
				msg_suc = sql_list_board(c, keyword)			
			elif len(msg_list) == 2 and hashtag in msg_list[1]:
				keyword = '%' + msg_list[1].replace('##', '', 1) + '%'
				print('keyword =', keyword)
				msg_suc = sql_list_board(c, keyword)				
			else:
				msg_suc = 'Usage: list-board ##<key>\r\n'
		elif msg_list[0] == 'list-post':
			if len(msg_list) == 2:
				board_name = msg_list[1]
				keyword = '%%'
				print('search without hashtag')
				msg_suc = sql_list_post(c, board_name, keyword)
			elif len(msg_list) >2 and hashtag in msg_list[2]:
				board_name = msg_list[1]
				msg_list[2] = msg_list[2].replace('##','',1)
				keyword = '%' + ' '.join(msg_list[2:len(msg_list)]) + '%'
				print('keyword =', keyword)
				msg_suc = sql_list_post(c, board_name, keyword)
			else:
				msg_suc = 'Usage: list-post <board-name> ##<key>\r\n'
		elif msg_list[0] == 'read':
			if len(msg_list) == 2:
				post_id = msg_list[1]
				msg_suc = sql_read_post(c, post_id)
			else:
				msg_suc = 'Usage: read <post-id> \r\n'
		elif msg_list[0] == 'delete-post':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) == 2:
				post_id = msg_list[1]
				msg_suc = sql_delete_post(conn, c, uid, post_id)
			else:
				msg_suc = 'Usage: delete-post <post-id> \r\n'
		elif msg_list[0] == 'update-post':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) > 3 and msg_list[2] == '--title':
				post_id = msg_list[1]
				update_data = ' '.join(msg_list[3:len(msg_list)])
				print('Updating post title =', update_data)
				msg_suc = sql_update_post_title(conn, c, uid, post_id, update_data)
			elif len(msg_list) > 3 and msg_list[2] == '--content':
				post_id = msg_list[1]
				update_data = ''.join(msg_list[3:len(msg_list)])
				print('Updating post content', update_data)
				msg_suc = sql_update_post_content(conn, c, uid, post_id, update_data)
			else:
				msg_suc = 'Usage: update-post <post-id> --title/content <new>\r\n'
		elif msg_list[0] == 'comment':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) > 2:
				post_id = msg_list[1]
				comment = ' '.join(msg_list[2:len(msg_list)])
				print('comment =', comment)
				msg_suc = sql_comment(conn, c, uid, post_id, comment)
			else:
				msg_suc = 'Usage: comment <post-id> <comment> \r\n'
		elif msg_list[0] == 'mail-to':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) > 5 and msg_list[2] == '--subject' and '--content' in msg_in:
				target_name = msg_list[1]
				print('target_name =', target_name)
				content_position = msg_list.index('--content')
				subject = ' '.join(msg_list[3:content_position])			
				print('subject =', subject)
				content = ' '.join(msg_list[content_position+1:len(msg_list)])
				print('content =', content)
				if subject == '' or content == '':
					msg_suc = 'Usage: create-post <board-name> --subject <subject> --content <content>\r\n'
				else:
					data = [target_name, subject, content]
					print('mail to...')
					msg_suc = sql_mail_to(conn, c, uid, data)
			else:
				msg_suc = 'Usage: mail-to <username> --subject <subject> --content <content> \r\n'
		elif msg_list[0] == 'list-mail':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) == 1:
				msg_suc = sql_list_mail(c, uid)
			else:
				msg_suc = 'Usage: list-mail \r\n'
		elif msg_list[0] == 'retr-mail':
			if uid == -1:
				msg_suc = 'Please login first.\r\n'
			elif len(msg_list) == 2 and msg_list[1].isdigit():
				mail_id = msg_list[1]
				msg_suc = sql_retr_mail(c, uid, mail_id)
			else:
				msg_suc = 'Usage: retr-mail <mail#> \r\n'
		elif msg_list[0] == 'enter&&space':
			msg_suc = ""
			pass
		else:
			msg_suc = 'Command not found\r\n'
		print('')
		return uid, msg_suc
#-------------------------------------------------------------

	conn = sqlite3.connect('Database.db')
	c = conn.cursor()
	print('Sql Connection Succeed')
	msg_out = '********************************\r\n' + '** Welcome to the BBS server. **\r\n' + '********************************\r\n'

	clientsocket.send(msg_out.encode('utf-8'))
	uid = -1

	while True:
		msg_out = '% '
		clientsocket.send(msg_out.encode('utf-8'))
		msg_in = clientsocket.recv(1024).decode('utf-8')	

		msg_in = msg_in.replace('\r','').replace('\n','')			
		print('msg_in = ',msg_in)
		if msg_in == 'exit':
			clientsocket.close()
			break		
		elif not msg_in or len(msg_in.split()) == 0:
			break
		else:				
			uid, msg_suc = string_processing(msg_in, conn, c, uid)
			if msg_suc != "":
				clientsocket.send(msg_suc.encode('utf-8'))
				msg_suc = ""
	clientsocket.close()

		
bind_ip = "0.0.0.0"
port = int(sys.argv[1])
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serversocket.bind((bind_ip, port))
serversocket.listen(20)
print('Waiting for connection...')

while True:
	clientsocket, addr = serversocket.accept();
	print('New Connection: %s' %str(addr))
	_thread.start_new_thread(new_client, (clientsocket, addr))