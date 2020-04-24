import socket
import sys
import time
import boto3

s3 = boto3.resource('s3')
target_bucket = None
	
def command(cmd, msg_in, s):
	if msg_in == 'Register successfully.\r\n':
		bucket_name = '0516319-' + cmd.split()[1] + '-0516319'		
		s3.create_bucket(Bucket = bucket_name)
	elif cmd.startswith('login') and msg_in.startswith('0516319'):
		target_bucket = s3.Bucket(msg_in)
		print(target_bucket)
		while True:
			try:
				msg_in = s.recv(1024).decode('utf-8')
				break
			except:
				pass
	elif cmd.startswith('logout') and msg_in.endswith('has logout'):
		target_bucket = None
		print('321')
	else:
		pass
	return msg_in


dst_ip = str(sys.argv[1])
port = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((dst_ip, port))
msg_in = s.recv(1024).decode('utf-8')
print(msg_in,end = "")
s.setblocking(0)

while True:
	while True:
		try:
			msg_in = s.recv(1024).decode('utf-8')
			break
		except:
			pass	
	print(msg_in ,end = "")
	print('please input')
	cmd = input()
	if not cmd or len(cmd.split()) == 0:
		cmd = 'enter&&space'
		s.send(cmd.encode('utf-8'))
	else:
		s.send(cmd.encode('utf-8'))
		while True:
			try:
				msg_in = s.recv(1024).decode('utf-8')
				break
			except:
				pass
		msg_in = command(cmd, msg_in, s)
		print(msg_in ,end = "")
		print(msg_in ,end = "")
		print('here')
		msg_in = ""


