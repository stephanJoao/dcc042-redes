import socket
import threading
import uuid
import random
from AES_Fragmentation import generate_aes_key, encrypt_message_aes, fragment_message, reassemble_and_decrypt_fragments

# Função para escutar conexões de outros peers
def listen_for_connections(peer_socket, peer_id, connected_peers, aes_key):
    peer_socket.listen(5)
    while True:
        conn, addr = peer_socket.accept()
        threading.Thread(target=handle_connection, args=(conn, addr, peer_id, connected_peers, aes_key)).start()

# Função para lidar com as conexões recebidas de outros peers
def handle_connection(conn, addr, peer_id, connected_peers, aes_key):
    try:
        # Recebe a mensagem do peer
        encrypted_fragment = conn.recv(1024)
        # Descriptografa o fragmento recebido
        decrypted_message = decrypt_message_aes(encrypted_fragment, aes_key)

        # Extrai o índice e o fragmento
        index, fragment = decrypted_message.split(':', 1)  # Separa o índice
        print(f'[{peer_id}] Received fragment {index}: {fragment}\n> ')
        
        # Aqui você pode armazenar os fragmentos e verificar se todos foram recebidos
        # Exemplo: received_fragments.append(f"{index}:{fragment}")
        # E ao receber todos os fragmentos, chame reassemble_and_decrypt_fragments()

    finally:
        conn.close()

# Função para converter os dados de peers recebidos em um dicionário
def parse_peers(peers_data):
    peers = {}
    if peers_data:
        for peer_info in peers_data.split(';'):
            peer_id, peer_ip, peer_port = peer_info.split(',')
            peers[peer_id] = (peer_ip, int(peer_port))
    return peers

# Função principal que inicializa o peer
def peer(peer_id, aes_key, rendezvous_host='127.0.0.1', rendezvous_port=12345):
    peer_port = random.randint(10000, 60000)
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind(('0.0.0.0', peer_port))

    connected_peers = {}
    # Adiciona a chave AES para a thread de escuta
    threading.Thread(target=listen_for_connections, args=(peer_socket, peer_id, connected_peers, aes_key)).start()

    rendezvous_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rendezvous_socket.connect((rendezvous_host, rendezvous_port))
    rendezvous_socket.sendall(f'{peer_id},{socket.gethostbyname(socket.gethostname())},{peer_port}'.encode())

    peers_data = rendezvous_socket.recv(1024).decode()
    connected_peers.update(parse_peers(peers_data))
    print(f'Initial peers: {connected_peers}\n> ')

    rendezvous_socket.close()
    return connected_peers

# Função para enviar uma mensagem para um peer específico
def peer_connection(addr, encrypted_message):
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect(addr)
        peer_socket.sendall(encrypted_message)
        peer_socket.close()
    except Exception as e:
        print(f'Could not connect to peer at {addr}: {e}')

# Função para enviar uma mensagem fragmentada para peers diferentes
def send_fragmented_message(connected_peers, message, aes_key):
    if not connected_peers:
        print("No peers connected. Cannot send the message.")
        return
    
    # Fragmenta a mensagem em partes menores
    fragments = fragment_message(message)
    
    # Para cada fragmento, criptografa e envia para um peer aleatório
    for i, fragment in enumerate(fragments):
        encrypted_fragment = encrypt_message_aes(f"{i}:{fragment}", aes_key)  # Criptografa o fragmento com AES
        peer_id, addr = random.choice(list(connected_peers.items()))  # Escolhe um peer aleatório
        print(f'Sending fragment {i} to peer {peer_id}')
        threading.Thread(target=peer_connection, args=(addr, encrypted_fragment)).start()

# Código principal que inicializa o peer e permite enviar mensagens
if __name__ == '__main__':
    peer_id = str(uuid.uuid4())[:6]
    print(f'Peer ID: {peer_id}')
    
    password = input("Enter a password for AES encryption: ")
    aes_key, salt = generate_aes_key(password)
    connected_peers = peer(peer_id, aes_key)

    while True:
        message = input("Message to send: ")
        send_fragmented_message(connected_peers, message, aes_key)
