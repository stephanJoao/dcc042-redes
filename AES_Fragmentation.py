from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

# Função para gerar chave AES a partir de uma senha usando derivação de chave (PBKDF2)
def generate_aes_key(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Gera um salt aleatório se não for fornecido
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # Algoritmo SHA-256 para derivar a chave
        length=32,  # Tamanho da chave AES (256 bits = 32 bytes)
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))  # Deriva a chave AES
    return key[:32], salt

# Função para criptografar uma mensagem com AES no modo CFB (Cipher Feedback Mode)
def encrypt_message_aes(message: str, key: bytes):
    try:
        iv = os.urandom(16)  # Gera um IV (vetor de inicialização) aleatório de 16 bytes
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Padding PKCS7 para ajustar o tamanho da mensagem ao bloco AES
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        
        encrypted_message = encryptor.update(padded_data) + encryptor.finalize()
        
        # Retorna o IV concatenado com a mensagem criptografada
        return iv + encrypted_message
    
    except ValueError as e:
        if "Invalid key size" in str(e):
            raise ValueError("Too long!")  # Mensagem de erro personalizada
        else:
            raise e

# Função para descriptografar uma mensagem com AES no modo CFB
def decrypt_message_aes(encrypted_message: bytes, key: bytes):
    iv = encrypted_message[:16]  # Extrai o IV dos primeiros 16 bytes
    encrypted_message = encrypted_message[16:]
    
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted_padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
    
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_message = unpadder.update(decrypted_padded_message) + unpadder.finalize()
    
    return decrypted_message.decode()

# Função para fragmentar uma mensagem em partes menores, com tamanho definido
def fragment_message(message, fragment_size=256):
    return [message[i:i+fragment_size] for i in range(0, len(message), fragment_size)]
