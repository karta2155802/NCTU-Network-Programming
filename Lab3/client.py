import socket
import sys
import time
import boto3
import os

s3 = boto3.resource('s3')
target_bucket = None

def mkdir():
    Pdata = "./.data"
    Ppost = "./.data/post"
    Pcomment = "./.data/comment"
    Pmail = "./.data/mail"
    try:
    	os.makedirs(Pdata)
    except FileExistsError:
    	pass
    try:
    	os.makedirs(Ppost)
    except FileExistsError:
    	pass
    try:
    	os.makedirs(Pcomment)
    except FileExistsError:
    	pass
    try:
    	os.makedirs(Pmail)
    except FileExistsError:
    	pass

def receive(len):
	while True:
		try:
			msg_in = s.recv(len).decode('utf-8')
			return msg_in
		except:
			pass

def DeleteMail(msg_in):
	msg_in_split = msg_in.split('###')
	mail_id_in_db = msg_in_split[1]

	os.remove("./.data/mail/m{}.txt".format(mail_id_in_db))
	target_bucket.Object("m{}.txt".format(mail_id_in_db)).delete()

	msg_in = msg_in_split[0]
	return msg_in

def RetrMail(msg_in):
	msg_in_split = msg_in.split('###')
	tmp_bucket = s3.Bucket(msg_in_split[2])
	mail_id_in_db = msg_in_split[1]
	print(msg_in_split[0])

	target_object = tmp_bucket.Object("m{}.txt".format(mail_id_in_db))
	object_content = target_object.get()['Body'].read().decode()
	print('    --')
	object_content_list = object_content.split('<br>')
	for i in object_content_list:
		print('    {}'.format(i))

	msg_in = ""
	return msg_in

def SendMail(cmd_list, msg_in):
	msg_in_split = msg_in.split('###')
	content_position = cmd_list.index('--content')
	content = ' '.join(cmd_list[content_position+1:len(cmd_list)])
	mail_id = msg_in_split[1]
	fp = open("./.data/mail/m{}.txt".format(mail_id), "w")
	fp.write(content)
	fp.close()
	tmp_bucket = s3.Bucket(msg_in_split[2])
	tmp_bucket.upload_file("./.data/mail/m{}.txt".format(mail_id), "m{}.txt".format(mail_id))
	return  msg_in_split[0]


def Comment(cmd_list, msg_in):
	msg_in_split = msg_in.split('###')
	name = msg_in_split[2]
	comment = ' '.join(cmd_list[2:len(cmd_list)])
	fp = open("./.data/comment/c{}.txt".format(cmd_list[1]), "a")
	fp.write('    {}: {}\n'.format(name, comment))
	fp.close()

	tmp_bucket = s3.Bucket(msg_in_split[1])
	tmp_bucket.upload_file("./.data/comment/c{}.txt".format(cmd_list[1]), "c{}.txt".format(cmd_list[1]))
	
	return msg_in_split[0]

def UpdatePost(cmd_list, msg_in):
	update_data = ' '.join(cmd_list[3:len(cmd_list)])
	fp = open("./.data/post/p{}.txt".format(cmd_list[1]), "w")
	fp.write(update_data)
	fp.close()
	target_bucket.upload_file("./.data/post/p{}.txt".format(cmd_list[1]), "p{}.txt".format(cmd_list[1]))

def ReadPost(cmd_list, msg_in):
	msg_in_split = msg_in.split('###')
	tmp_bucket = s3.Bucket(msg_in_split[1])
	print(msg_in_split[0])

	target_object1 = tmp_bucket.Object("p{}.txt".format(cmd_list[1]))
	object_content = target_object1.get()['Body'].read().decode()
	target_object2 = tmp_bucket.Object("c{}.txt".format(cmd_list[1]))
	object_comment = target_object2.get()['Body'].read().decode()

	print('    --')
	object_content_list = object_content.split('<br>')
	for i in object_content_list:
		print('    {}'.format(i))
	print('    --')
	print(object_comment, end='')
	msg_in = ""
	return msg_in

def DeletePost(cmd_list):
	os.remove("./.data/post/p{}.txt".format(cmd_list[1]))
	os.remove("./.data/comment/c{}.txt".format(cmd_list[1]))
	target_bucket.Object("p{}.txt".format(cmd_list[1])).delete()
	target_bucket.Object("c{}.txt".format(cmd_list[1])).delete()

def CreatePost(cmd_list, msg_in):
	post_id = msg_in.split('###')[1]
	content_position = cmd_list.index('--content')
	content = ' '.join(cmd_list[content_position+1:len(cmd_list)])

	fp = open("./.data/post/p{}.txt".format(post_id), "w")
	fp.write(content)
	fp.close()
	fp = open("./.data/comment/c{}.txt".format(post_id), "w")
	fp.close()
	target_bucket.upload_file("./.data/post/p{}.txt".format(post_id), "p{}.txt".format(post_id))
	target_bucket.upload_file("./.data/comment/c{}.txt".format(post_id), "c{}.txt".format(post_id))
	msg_in = msg_in.split('###')[0]
	return msg_in

def command(cmd, msg_in, s, target_bucket):
	cmd_list = cmd.split()
	if msg_in == 'Register successfully.\r\n':
		bucket_name = '0516319-' + cmd_list[1] + '-0516319'		
		s3.create_bucket(Bucket = bucket_name)
	elif cmd.startswith('login') and msg_in.startswith('Welcome, '):
		bucket_name = msg_in.split('###')[1]
		target_bucket = s3.Bucket(bucket_name)
		msg_in = msg_in.split('###')[0]		
	elif cmd.startswith('logout') and msg_in.startswith('Bye'):
		target_bucket = None
	elif cmd.startswith('create-post') and msg_in.startswith('Create post successfully'):
		msg_in = CreatePost(cmd_list, msg_in)		
	elif cmd.startswith('delete-post') and msg_in == 'Delete successfully.\r\n':
		DeletePost(cmd_list)
	elif cmd.startswith('read') and not (msg_in == 'Post does not exist.\r\n' or msg_in == 'Usage: read <post-id> \r\n'):
		msg_in = ReadPost(cmd_list, msg_in)
	elif cmd.startswith('update-post') and '--content' in cmd and msg_in == 'Update successfully.\r\n':
		UpdatePost(cmd_list, msg_in)
	elif cmd.startswith('comment') and msg_in.startswith('Comment successfully'):
		msg_in = Comment(cmd_list, msg_in)
	elif cmd.startswith('mail-to') and msg_in.startswith('Sent successfully'):
		msg_in = SendMail(cmd_list, msg_in)	
	elif cmd.startswith('retr-mail') and msg_in.endswith('0516319'):
		msg_in = RetrMail(msg_in)
	elif cmd.startswith('delete-mail') and msg_in.startswith('Mail deleted'):
		msg_in = DeleteMail(msg_in)	
	elif cmd == 'exit':
		sys.exit()
	else:
		pass
	return msg_in, target_bucket


dst_ip = str(sys.argv[1])
port = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((dst_ip, port))
msg_in = s.recv(1024).decode('utf-8')
print(msg_in,end = "")
s.setblocking(0)
mkdir()

while True:
	cmd = input("% ")
	if not cmd or len(cmd.split()) == 0:
		pass
	else:
		s.send(cmd.encode('utf-8'))
		msg_in = receive(8192);
		msg_in, target_bucket = command(cmd, msg_in, s, target_bucket)
		if msg_in != "":
			print(msg_in ,end = "")
