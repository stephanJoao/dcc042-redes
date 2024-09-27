import socket
import threading
import uuid
import random
from encryptionRSA import *
from encryptionAES import *
from sympy import public
import os


def pick_random_key(d,destinatario):
    # Get all the keys from the dictionary
    keys = list(d.keys())
    # Return a random choice from the keys
    hops = destinatario
    while(hops == destinatario):
        hops = random.choice(keys)
    return hops

def listen_for_connections(peer_socket, peer_id, connected_peers,arrayList):
    peer_socket.listen(5)
    while True:
        conn, addr = peer_socket.accept()
        threading.Thread(
            target=handle_connection,
            args=(conn, addr, peer_id, connected_peers,arrayList),
        ).start()


def handle_connection(conn, addr, peer_id, connected_peers, arrayList):
    try:
        message = conn.recv(1024).decode()
        print(f"mensagem no handle: {message}")
        if message.startswith("PEER_LIST;"):
            _, peers_data = message.split(";", 1)
            if peers_data:
                new_peers = parse_peers(peers_data)
                connected_peers.clear()
                connected_peers.update(new_peers)
                print(f"Updated peers list: {connected_peers}")
        
        else:
            sizeidpeer1= int(message[0])
            sizeidpeer2= int(message[sizeidpeer1:sizeidpeer1+1])
            sizeHops =int(message[-1])
            quantHops =int(message[-int(sizeHops)-1:-1])
            
            #Verifica se é apenas um Hop 
            if(quantHops>0):
                print(f"HOP -> {message}")
                message = message[:-int(sizeHops)-1]
                quantHops = quantHops - 1
                sizeHops = len(str(quantHops))
                message = message + str(quantHops) + str(sizeHops)
                if quantHops != 0:
                    hopMessage(connected_peers,message,str(message[1:sizeidpeer1]))
                else:
                    realAddr=tuple(connected_peers[message[1:sizeidpeer1]][:-1])
                    peer_connection(realAddr,message)
            else:
                if "SK:" in message:
                    data = message.split("SK:")
                    decryptMessage = data[1]
                    private_key = read_private_key(peer_id)
                    encryptMsg = decryptMessage[:-int(sizeHops)-1]
                    trueMessage = decrypt_message(private_key, encryptMsg)
                    sessioKey = bytes.fromhex(trueMessage)
                    with open(f'pasta/{peer_id}/aes_{message[1:sizeidpeer1]}_{message[1+sizeidpeer1:sizeidpeer1+sizeidpeer2]}_key.key', 'wb') as key_file:
                        key_file.write(sessioKey)
                else:
                    if str(message[1:sizeidpeer1]) == str(peer_id):
                        encryptMsg = message[sizeidpeer1+sizeidpeer2:-int(sizeHops)-1]
                        sessioKey = ""
                        with open(f'pasta/{message[1+sizeidpeer1:sizeidpeer1+sizeidpeer2]}/aes_{message[1:sizeidpeer1]}_{message[1+sizeidpeer1:sizeidpeer1+sizeidpeer2]}_key.key', 'rb') as key_file:
                            sessioKey = key_file.read()

                        encryptMsg = bytes.fromhex(encryptMsg)

                        decryptMessage=decrypt_message_aes(encryptMsg,sessioKey) #.encode(encoding="utf-8")
                        private_key = read_private_key(peer_id)
                        trueMessage = decrypt_message(private_key, decryptMessage)
                        arrayList.append(trueMessage)       
                        print(f"[chat]: mensagem recebida original-> {trueMessage}")
                        print(arrayList)
                    else:
                        print(f"[chat]: mensagemrecebida com criptografia-> {message}")
    finally:
        conn.close()


def parse_peers(peers_data):
    peers = {}
    if peers_data:
        for peer_info in peers_data.split(";"):
            peer_id, peer_ip, peer_port, public_key = peer_info.split(",")
            peers[peer_id] = (peer_ip, int(peer_port), public_key)
    return peers


def peer(
    peer_id, public_key, rendezvous_host="127.0.0.1", rendezvous_port=12345
):
    peer_port = random.randint(10000, 60000)
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind(("0.0.0.0", peer_port))
    arrayList = []
    connected_peers = {}
    threading.Thread(
        target=listen_for_connections,
        args=(peer_socket, peer_id, connected_peers,arrayList),
    ).start()

    # Connect to rendezvous server
    rendezvous_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rendezvous_socket.connect((rendezvous_host, rendezvous_port))
    rendezvous_socket.sendall(
        f"{peer_id},{socket.gethostbyname(socket.gethostname())},{peer_port},{public_key}"
        .encode()
    )

    peers_data = rendezvous_socket.recv(1024).decode()
    connected_peers.update(parse_peers(peers_data))
    print(f"Initial peers: {connected_peers}\n> ")

    rendezvous_socket.close()

    return connected_peers


def peer_connection(addr, message):
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect(addr)

        sizeId= int(message[0])
        realAddr=tuple(connected_peers[message[1:sizeId]][:-1])
        peer_socket.sendto(message.encode(),realAddr)
        peer_socket.close()
    except Exception as e:
        print(f"Could not connect to peer at {addr}: {e}")
    


def hopMessage(connected_peers,trueMessage,destinatario):
    destinatoriohop = pick_random_key(connected_peers,destinatario)
    print(destinatoriohop)
    realAddr=tuple(connected_peers[destinatoriohop][:-1])
    peer_connection(realAddr,trueMessage)
    
def send_message(connected_peers, message,peer_id):
    #Propriedade para verificar se ID foi encontrado
    IdEncontrado = False
    print("Para qual Peer Id deseja enviar a mensagem:")
    destinatario = input()
    peer_idSize = len(peer_id)+1
    for pid, addr in connected_peers.items():
        #Se ID igual definido envia mensagem para o destinatario
        if(pid == destinatario):
            realAddr = addr[:-1]
            realAddr=tuple(realAddr)
            #Contador a ser passado para o HOP 
            contHop = len(connected_peers.items())-1
            lenHop = len(str(contHop))
            #Chave de gerada
            session_key, salt = generate_aes_key(pid)

            with open(f'pasta/{peer_id}/aes_{pid}_{peer_id}_key.key', 'wb') as key_file:
                key_file.write(session_key)

            randPeerKey = read_public_key(pid)
            sizeId = len(pid)+1

            message1 = session_key.hex()
            message1 = encrypt_message(randPeerKey,message1)
            trueMessage = str(sizeId)+str(pid)+str(peer_idSize)+peer_id+"SK:"+str(message1) + str(0) + str(1)
            peer_connection(realAddr,trueMessage)

            #separação
            # messages = fragment_message(message)
            # for eachMessage in messages
            message = encrypt_message(randPeerKey,message)
            message = encrypt_message_aes(message,session_key)
            message = message.hex()
            trueMessage = str(sizeId)+str(pid)+str(peer_idSize)+peer_id+str(message) 

            trueMessage = trueMessage + str(contHop) + str(lenHop) 
            hopMessage(connected_peers,trueMessage,destinatario)
            
            #Envia mensagem  
            # threading.Thread(target=peer_connection, args=(realAddr, trueMessage)).start()
            IdEncontrado = True
            print("Mensagem enviada")
    #Caso nao tenha achado o ID retorna mensagem         
    if(IdEncontrado != True):
        print("ID não encontrado")            

if __name__ == "__main__":
    peer_id = str(uuid.uuid4())[:6]
    
    private_key,public_key = generate_keys()
    listOfSessionKeys = []
    # private_key, public_key= generate_keys()
    save_public_key(public_key, peer_id)
    save_private_key(private_key, peer_id)
    connected_peers = peer(peer_id, public_key)
    print(
        f"Peer ID: {peer_id}\nPublic key{public_key}\nPrivate key{private_key}"
    )
    while True:
        message = input("> ")
        send_message(connected_peers, message,peer_id)
        


#função encripta com chave publica de outros
#função decripta mensagem quando chega
#função encripta mensagem com chave de sessão
#Função gera chave de seção