import socket

def client_program():
	host = socket.gethostname()  
	print(f"Host: {host}")
	port = 12345  

	# conecta ao servidor
	client_socket = socket.socket()  
	client_socket.connect((host, port))
	print(f"Connected to {host} on port {port}")

	while True:
		# lê mensagem 
		message = input("Enter a message: ")

		# envia mensagem
		client_socket.send(message.encode())  

		# se for "bye", fecha conexão
		if message.lower().strip() == "bye":
			break

		# pega resposta
		data = client_socket.recv(1024).decode()
		print('[' + host + ']: ' + data)

	client_socket.close()


if __name__ == "__main__":
	client_program()