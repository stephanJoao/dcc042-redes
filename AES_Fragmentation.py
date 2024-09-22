from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import hashlib

# Função para gerar chave AES a partir de uma senha usando derivação de chave (PBKDF2)
def generate_aes_key(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Gera um salt aleatório se não for fornecido
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # O algoritmo SHA-256 para derivar a chave
        length=32,  # Tamanho da chave AES (256 bits = 32 bytes)
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))  # Deriva a chave AES a partir da senha
    return key[:32], salt

# Função para criptografar uma mensagem com AES no modo CFB (Cipher Feedback Mode)
def encrypt_message_aes(message: str, key: bytes):
    try:
        # Gera um valor IV (vetor de inicialização) aleatório de 16 bytes
        iv = os.urandom(16)
        
        # Cria um cifrador AES no modo CFB usando a chave e o IV gerados
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Usa padding PKCS7 para ajustar o tamanho da mensagem ao tamanho do bloco AES
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        
        # Criptografa a mensagem (com padding)
        encrypted_message = encryptor.update(padded_data) + encryptor.finalize()
        
        # Retorna o IV concatenado com a mensagem criptografada (o IV é necessário para a descriptografia)
        return iv + encrypted_message
    
    except ValueError as e:
        if "Invalid key size" in str(e):
            raise ValueError("Too long!")  # Mensagem de erro personalizada
        else:
            raise e  # Relança outros erros

# Função para descriptografar uma mensagem com AES no modo CFB
def decrypt_message_aes(encrypted_message: bytes, key: bytes):
    # Separa o IV da mensagem criptografada (os primeiros 16 bytes são o IV)
    iv = encrypted_message[:16]
    encrypted_message = encrypted_message[16:]
    
    # Cria o objeto de descriptografia AES no modo CFB com o IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Descriptografa a mensagem
    decrypted_padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
    
    # Remove o padding PKCS7 para recuperar a mensagem original
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_message = unpadder.update(decrypted_padded_message) + unpadder.finalize()
    
    # Retorna a mensagem original descriptografada como string
    return decrypted_message.decode()

# Função para fragmentar uma mensagem em partes menores, com tamanho definido
def fragment_message(message, fragment_size=256):
    # Divide a mensagem em pedaços de 'fragment_size' caracteres
    return [message[i:i+fragment_size] for i in range(0, len(message), fragment_size)]
