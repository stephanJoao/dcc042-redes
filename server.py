import socket
import threading

def handle_client(client_socket, address):
	try:
		print('Accepted connection from client', address) 
		
		while True:
			# receive message from client
			data = client_socket.recv(1024).decode()
			print('Received message from client:', data)

			# if message is "bye", exit the loop
			if data.lower().strip() == 'bye':
				print(f'Client {address} has disconnected')
				break
			# if starts with "echo", send response to client
			elif data.lower().strip().startswith('echo '):
				data = data[data.find('echo')+5:]
				print('Sending response to client')
				client_socket.send(data.encode())
				
	finally:
		# close connection
		print('Closing connection with client', address)
		client_socket.close()

def server_program():
	# create socket
	port = 42069
	host = socket.gethostname()
	server_socket = socket.socket() 
	print('Started server on port', port) 
		
	server_socket.bind((host, port))
	server_socket.listen(5)  # listening for multiple connections

	started = True

	# keep listening for incoming connections
	while True:
		# create client socket
		client_socket, address = server_socket.accept()

		# handle client connection in a new thread
		client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
		client_thread.start()  # start the thread to handle the client


if __name__ == "__main__":
	server_program()