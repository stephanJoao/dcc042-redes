import socket
import threading
import uuid
import random
from AES_Fragmentation import generate_aes_key, encrypt_message_aes, fragment_message 

# Função para escutar conexões de outros peers
def listen_for_connections(peer_socket, peer_id, connected_peers):
    # Deixa o socket no modo de escuta para aceitar conexões
    peer_socket.listen(5)
    while True:
        # Aceita uma nova conexão de outro peer
        conn, addr = peer_socket.accept()
        # Cria uma nova thread para lidar com a conexão recebida
        threading.Thread(target=handle_connection, args=(conn, addr, peer_id, connected_peers)).start()

# Função para lidar com as conexões recebidas de outros peers
def handle_connection(conn, addr, peer_id, connected_peers):
    try:
        # Recebe a mensagem do peer e decodifica
        message = conn.recv(1024).decode()
        if message.startswith('PEER_LIST;'):
            # Atualiza a lista de peers se receber uma lista de peers
            _, peers_data = message.split(';', 1)
            if peers_data:
                new_peers = parse_peers(peers_data)
                connected_peers.clear()
                connected_peers.update(new_peers)
                print(f'Updated peers list: {connected_peers}\n> ')
        else:
            # Exibe a mensagem recebida
            print(f'[{peer_id}]: {message}\n> ')
    finally:
        # Fecha a conexão após o tratamento
        conn.close()

# Função para converter os dados de peers recebidos em um dicionário
def parse_peers(peers_data):
    peers = {}
    if peers_data:
        # Divide os dados de peers e armazena-os em um dicionário
        for peer_info in peers_data.split(';'):
            peer_id, peer_ip, peer_port = peer_info.split(',')
            peers[peer_id] = (peer_ip, int(peer_port))
    return peers

# Função principal que inicializa o peer
def peer(peer_id, rendezvous_host='127.0.0.1', rendezvous_port=12345):
    # Define uma porta aleatória para o peer
    peer_port = random.randint(10000, 60000)
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind(('0.0.0.0', peer_port))

    connected_peers = {}
    # Inicia a thread para escutar conexões de outros peers
    threading.Thread(target=listen_for_connections, args=(peer_socket, peer_id, connected_peers)).start()

    # Conecta ao servidor rendezvous para registrar o peer e obter a lista de peers
    rendezvous_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rendezvous_socket.connect((rendezvous_host, rendezvous_port))
    rendezvous_socket.sendall(f'{peer_id},{socket.gethostbyname(socket.gethostname())},{peer_port}'.encode())

    # Recebe a lista inicial de peers conectados
    peers_data = rendezvous_socket.recv(1024).decode()
    connected_peers.update(parse_peers(peers_data))
    print(f'Initial peers: {connected_peers}\n> ')

    # Fecha a conexão com o servidor rendezvous após obter a lista de peers
    rendezvous_socket.close()

    return connected_peers

# Função para enviar uma mensagem para um peer específico
def peer_connection(addr, encrypted_message):
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect(addr)  # Conecta ao peer
        peer_socket.sendall(encrypted_message)  # Envia a mensagem criptografada
        peer_socket.close()
    except Exception as e:
        print(f'Could not connect to peer at {addr}: {e}')

# Função para enviar uma mensagem fragmentada para peers diferentes
def send_fragmented_message(connected_peers, message, aes_key):
    # Verifica se há peers conectados antes de tentar enviar a mensagem
    if not connected_peers:
        print("No peers connected. Cannot send the message.")
        return  # Sai da função se não houver peers conectados
    
    # Fragmenta a mensagem em partes menores
    fragments = fragment_message(message)
    
    # Para cada fragmento, criptografa e envia para um peer aleatório
    for i, fragment in enumerate(fragments):
        encrypted_fragment = encrypt_message_aes(f"{i}:{fragment}", aes_key)  # Criptografa o fragmento com AES
        # Escolhe um peer aleatório para enviar o fragmento
        peer_id, addr = random.choice(list(connected_peers.items()))
        print(f'Sending fragment {i} to peer {peer_id}')
        # Envia o fragmento usando uma nova thread para cada envio
        threading.Thread(target=peer_connection, args=(addr, encrypted_fragment)).start()


# Código principal que inicializa o peer e permite enviar mensagens
if __name__ == '__main__':
    # Gera um ID único para o peer
    peer_id = str(uuid.uuid4())[:6]
    
    # Inicializa o peer e obtém a lista de peers conectados
    connected_peers = peer(peer_id)
    print(f'Peer ID: {peer_id}')
    
    # Solicita uma senha do usuário para gerar a chave AES
    password = input("Enter a password for AES encryption: ")
    aes_key, salt = generate_aes_key(password)  # Gera a chave AES a partir da senha fornecida

    # Loop para enviar mensagens continuamente
    while True:
        message = input("Message to send: ")
        send_fragmented_message(connected_peers, message, aes_key)  # Envia a mensagem fragmentada
