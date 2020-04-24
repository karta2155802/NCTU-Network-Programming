import socket
import sys
import time
#import boto3

	


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
	
	s.send(cmd.encode('utf-8'))
	if not cmd or len(cmd.split()) == 0:
		print('this is enter or space')
		
	while True:
		try:
			msg_in = s.recv(1024).decode('utf-8')
			break
		except:
			pass
	print(msg_in ,end = "")
