import socket
import threading
import rsa
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Tamanho dos fragmentos das mensagens
FRAGMENT_SIZE = 128

# Gerar chave RSA
(pub_key, priv_key) = rsa.newkeys(512)

# Função para criptografar dados usando AES
def encrypt_aes(key, plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return iv + ciphertext

# Função para descriptografar dados usando AES
def decrypt_aes(key, ciphertext):
    iv = ciphertext[:16]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext[16:]) + decryptor.finalize()

# Função para dividir a mensagem em fragmentos
def fragment_message(message):
    fragments = [message[i:i+FRAGMENT_SIZE] for i in range(0, len(message), FRAGMENT_SIZE)]
    return fragments

# Função para reconstruir a mensagem a partir dos fragmentos
def reconstruct_message(fragments):
    return b''.join(fragments)

# Função para tratar a conexão de um nó
def handle_client(client_socket, session_key):
    fragments = []

    while True:
        fragment = client_socket.recv(1024)
        if not fragment:
            break
        # Descriptografa o fragmento recebido
        decrypted_fragment = decrypt_aes(session_key, fragment)
        fragments.append(decrypted_fragment)

    # Reconstrói a mensagem original
    original_message = reconstruct_message(fragments)
    print(f"[+] Mensagem recebida: {original_message.decode('utf-8')}")

    client_socket.close()

# Função para iniciar o servidor P2P
def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"[*] Servidor escutando na porta {port}...")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Conexão recebida de {addr}")

        # Recebe a chave de sessão criptografada
        encrypted_session_key = client_socket.recv(1024)
        session_key = rsa.decrypt(encrypted_session_key, priv_key)

        client_handler = threading.Thread(target=handle_client, args=(client_socket, session_key))
        client_handler.start()

# Função para enviar uma mensagem para outro nó
def send_message(target_ip, target_port, message):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_ip, target_port))

    # Cria uma chave de sessão AES e criptografa com RSA
    session_key = os.urandom(16)
    encrypted_session_key = rsa.encrypt(session_key, pub_key)

    # Envia a chave de sessão criptografada
    client.send(encrypted_session_key)

    # Fragmenta e criptografa a mensagem
    fragments = fragment_message(message.encode('utf-8'))
    for fragment in fragments:
        encrypted_fragment = encrypt_aes(session_key, fragment)
        client.send(encrypted_fragment)

    client.close()

# Código para iniciar o servidor e enviar uma mensagem
if __name__ == "__main__":
    # Iniciar servidor P2P em uma thread separada
    port = 9999
    server_thread = threading.Thread(target=start_server, args=(port,))
    server_thread.start()

    # Enviar mensagem para outro nó
    target_ip = "127.0.0.1"
    target_port = 9999
    message = "Olá, esta é uma mensagem fragmentada e criptografada!"
    send_message(target_ip, target_port, message)