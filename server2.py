import socket
import threading

def handle_client(client_socket, address):
	try:
		print('Accepted connection from client', address) 
		
		while True:
			# Receive message from client
			data = client_socket.recv(1024).decode()
			print('Received from client:', data)

			# Send response
			response = data  # Echoing back the received data
			print('Sending response to client')
			client_socket.send(response.encode())
	finally:
		# Close connection
		print('Closing connection with client', address)
		client_socket.close()

def server_program():
	# Create socket
	port = 12345
	host = socket.gethostname()
	server_socket = socket.socket() 
	print('Started server on port', port) 
		
	server_socket.bind((host, port))
	server_socket.listen(5)  # Listening for multiple connections

	# Keep listening for incoming connections
	while True:
		# Create client socket
		client_socket, address = server_socket.accept()

		# Handle client connection in a new thread
		client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
		client_thread.start()  # Start the thread to handle the client

if __name__ == "__main__":
	server_program()
