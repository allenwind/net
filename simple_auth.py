import hmac
import os

from socket import socket, AF_INET, SOCK_STREAM
from socketserver import TCPServer

#both know secret_key

def client_authenticate(connection, secret_key):
	message = connection.recv(320)
	hash_ = hmac.new(secret_key, message)
	digest = hash_.digeset()
	connection.send(digest)

def server_authenticate(connection, secret_key):
	message = os.urandom(320)
	connection.send(message)
	hash_ = hmac.new(secret_key, message)
	digest = hash_.digest()
	response = connection.recv(len(digest))
	return hmac.compare_digest(digest, response)

def echo_handler(client_sock):
	if not server_authenticate(client_sock, secret_key):
		client_sock.close()
		return 
	while True:
		msg = client_sock.recv(1024)
		if not msg:
			break
		client_sock.sendall(msg)

def echo_server(address):
	s = socket(AF_INET, SOCK_STREAM)
	s.bind(address)
	s.listen(5)
	while True:
		client, addr = s.accept()
		echo_handler(client)

#use auth in TCPServer
class TCPAuthServer(TCPServer):
	_AUTH_LENGTH = 320
	def verify_request(self, request, client_address):
		message = os.urandom(_AUTH_LENGTH)
		request.send(message)
		hash_ = hmac.new(secret_key, message)
		digest = hash_.digest()
		response = request.recv(len(digest))
		status = hmac.compare_digest(digest, response)
		#add client_address to auth queue
		return status

class ThreadingTCPAuthServer(ThreadingMixIn, TCPAuthServer): pass







if __name__ == '__main__':
	secret_key = b'task'

	echo_server(('localhost', 8080))