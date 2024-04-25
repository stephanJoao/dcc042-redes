import socket

def server_program():
	# cria socket
	port = 12345
	host = socket.gethostname()
	server_socket = socket.socket() 
	print('Started server on port', port) 
		 
	server_socket.bind((host, port))
	server_socket.listen(1)

	# fica escutando
	while True:
		# cria socket do client
		client_socket, address = server_socket.accept()
		print('Accepted connection from client', address) 
		
		# mensagem do client
		data = client_socket.recv(1024).decode()
		print('Received from client:', data)

		# envia resposta
		print('Sending response to client')
		client_socket.send(data.encode())

		# fecha conexão
		print('Closing connection with client')
		client_socket.close()	


if __name__ == "__main__":
	server_program() 