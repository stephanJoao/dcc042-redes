# Import necessary modules from pycryptodomepy
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from binascii import hexlify, unhexlify
import os

# Function to generate RSA public and private keys
def generate_keys():
    # Generate RSA key pair (1024 bits)
    key = RSA.generate(1024)
    private_key = key
    public_key = key.publickey()
    return private_key, public_key

# Function to encrypt a message using the public key
def encrypt_message(public_key, message):
    # Create a PKCS1_OAEP cipher object with the public key
    cipher_rsa = PKCS1_OAEP.new(public_key)
    # Encrypt the message
    encrypted = cipher_rsa.encrypt(message.encode('utf-8'))
    # Return the encrypted message as hexadecimal
    return hexlify(encrypted).decode('utf-8')

# Function to decrypt a message using the private key
def decrypt_message(private_key, encrypted_message):
    # Convert the encrypted message from hexadecimal to binary
    encrypted_bytes = unhexlify(encrypted_message)
    # Create a PKCS1_OAEP cipher object with the private key

    cipher_rsa = PKCS1_OAEP.new(private_key)
    # Decrypt the message
    decrypted = cipher_rsa.decrypt(encrypted_bytes)
    # Return the decrypted message as a UTF-8 string

    return decrypted.decode('utf-8')

def save_private_key(private_key, peer_id, pwd=b'secret'):
    # Save private key with encryption and protection parameters
    if not os.path.exists(f"pasta/{peer_id}/"):
        os.makedirs(f"pasta/{peer_id}/")
    f = open(f"pasta/{peer_id}/myprivatekey{peer_id}.pem", "wb")
    data = private_key.export_key(passphrase=pwd,
                                pkcs=8,
                                protection='PBKDF2WithHMAC-SHA512AndAES256-CBC',
                                prot_params={'iteration_count': 131072})
    f.write(data)

# Function to save the public key
def save_public_key(public_key, peer_id):
    # Save public key in a PEM file without encryption
    if not os.path.exists(f"pasta/{peer_id}/"):
        os.makedirs(f"pasta/{peer_id}/")
    f = open(f"pasta/{peer_id}/mypublickey{peer_id}.pem", "wb") 
    data = public_key.export_key()
    f.write(data)

def read_private_key(peer_id, pwd=b'secret'):
    # Read and import the private key from the file
    if not os.path.exists(f"pasta/{peer_id}/"):
        os.makedirs(f"pasta/{peer_id}/")
    f = open(f"pasta/{peer_id}/myprivatekey{peer_id}.pem", "rb") 
    data = f.read()
    private_key = RSA.import_key(data, passphrase=pwd)
    return private_key

# Function to read the public key
def read_public_key(peer_id):
    # Read and import the public key from the file
    if not os.path.exists(f"pasta/{peer_id}/"):
        os.makedirs(f"pasta/{peer_id}/")
    f = open(f"pasta/{peer_id}/mypublickey{peer_id}.pem", "rb") 
    data = f.read()
    public_key = RSA.import_key(data)
    return public_key


    # Example usage
if __name__ == "__main__":
    mykey = None
    # Generate keys
    private_key, public_key = generate_keys()
    print(type(private_key.export_key))
    print(public_key.export_key)
    # Example message
    pwd = b'secret'
    with open("myprivatekeyRedes.pem", "wb") as f:
        data = private_key.export_key(passphrase=pwd,
                                    pkcs=8,
                                    protection='PBKDF2WithHMAC-SHA512AndAES256-CBC',
                                    prot_params={'iteration_count':131072})
        f.write(data)
    
    pwd = b'secret'
    with open("myprivatekeyRedes.pem", "rb") as f:
        data = f.read()
        mykey = RSA.import_key(data, pwd)

    with open("mypublickeyRedes.pem", "wb") as f:
        data = public_key.public_key().export_key()
        f.write(data)

    with open("mypublickeyRedes.pem", "rb") as f:
        data = f.read()
        mykey = RSA.import_key(data, pwd)    
    print(mykey.export_key)

    message = "Hello, this is a secret message."
    
    # Encrypt the message using the public key
    encrypted_message = encrypt_message(public_key, message)
    print("Encrypted message:", encrypted_message)
    print(type(encrypted_message))
    # Decrypt the message using the private key
    decrypted_message = decrypt_message(private_key, encrypted_message)
    print("Decrypted message:", decrypted_message)

