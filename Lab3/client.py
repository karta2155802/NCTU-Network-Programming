import socket
import sys
import time
import boto3

	
def command(cmd, msg_in):
	if msg_in == 'Register successfully.\r\n':
		bucket_name = '0516319-' + cmd.split()[1] + '-0516319'
		s3 = boto3.resource('s3')
		s3.create_bucket(Bucket = bucket_name)


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
		command(cmd, msg_in)
		print(msg_in ,end = "")

