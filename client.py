import socket

def client_program():
	host = socket.gethostname()  
	port = 42069  

	# create client socket
	client_socket = socket.socket()  

	try:
		# connect to the server
		client_socket.connect((host, port))
		print(f"Connected to {host} on port {port}")

		while True:
			# Read a message from the user
			message = input(f'[client]: ')

			# send message to the server
			client_socket.send(message.encode())  

			# if message is "bye", exit the loop
			if message.lower().strip() == "bye":
				print("Closing connection...")
				break
			# if message starts with "echo", receive response from the server
			elif message.lower().strip().startswith('echo '):
				data = client_socket.recv(1024).decode()
				print(f'[{host}]: {data}')
		
	except ConnectionError:
		print("Connection error. Is the server running?")
		
	finally:
		# Ensure the connection is closed
		client_socket.close()
		print("Connection closed.")

if __name__ == "__main__":
	client_program()