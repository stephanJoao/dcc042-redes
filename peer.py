import socket
import threading
import uuid
import random
from encryptionRSA import *
from sympy import public

def pick_random_key(d,destinatario):
    # Get all the keys from the dictionary
    keys = list(d.keys())
    # Return a random choice from the keys
    hops = destinatario
    while(hops == destinatario):
        hops = random.choice(keys)
    return hops

def listen_for_connections(peer_socket, peer_id, connected_peers):
    peer_socket.listen(5)
    while True:
        conn, addr = peer_socket.accept()
        threading.Thread(
            target=handle_connection,
            args=(conn, addr, peer_id, connected_peers),
        ).start()


def handle_connection(conn, addr, peer_id, connected_peers):
    try:
        message = conn.recv(1024).decode()
        if message.startswith("PEER_LIST;"):
            _, peers_data = message.split(";", 1)
            if peers_data:
                new_peers = parse_peers(peers_data)
                connected_peers.clear()
                connected_peers.update(new_peers)
                print(f"Updated peers list: {connected_peers}")
        else:
            sizeId= int(message[0])
            sizeHops =int(message[-1])
            quantHops =int(message[-int(sizeHops)-1:-1])
            
            #Verifica se é apenas um Hop 
            if(quantHops>0):
                print(f"HOP -> {message}")
                message = message[:-int(sizeHops)-1]
                quantHops = quantHops - 1
                sizeHops = len(str(quantHops))
                message = message + str(quantHops) + str(sizeHops)
                hopMessage(connected_peers,message,str(message[1:sizeId]))
            else:
                if str(message[1:sizeId]) == str(peer_id):
                    #encryptMsg = message[sizeId::-int(sizeHops)-1]
                    #private_key = read_private_key(peer_id)
                    #trueMessage = decrypt_message(private_key, encryptMsg)
                    print(f"[chat]: mensagem a ser recebida -> {message}")
                else:
                    print(f"[chat]: mensagem a ser recebida -> {message}")
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

    connected_peers = {}
    threading.Thread(
        target=listen_for_connections,
        args=(peer_socket, peer_id, connected_peers),
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
        peer_socket.sendall(message.encode())
        peer_socket.close()
    except Exception as e:
        print(f"Could not connect to peer at {addr}: {e}")


def hopMessage(connected_peers,trueMessage,destinatario):
    destinatoriohop = pick_random_key(connected_peers,destinatario)
    print("Destinatario")
    print(destinatoriohop)
    realAddr=tuple(connected_peers[destinatoriohop][:-1])
    peer_connection(realAddr,trueMessage)
    #threading.Thread(target=peer_connection, args=(realAddr, trueMessage)).start()
    
def send_message(connected_peers, message):
    #Propriedade para verificar se ID foi encontrado
    IdEncontrado = False
    print("Para qual Peer Id deseja enviar a mensagem:")
    destinatario = input()
 
    for pid, addr in connected_peers.items():
        #Se ID igual definido envia mensagem para o destinatario
        if(pid == destinatario):
            realAddr = addr[:-1]
            realAddr=tuple(realAddr)
            #vai enviar a chave de sessao a ser implementado posteriomente
            #threading.Thread(target=peer_connection, args=(realAddr,"chave")).start()
            
            #randPeerKey = read_public_key(pid)
            #message = encrypt_message(randPeerKey,message)
            sizeId = len(pid)+1
            
            trueMessage = str(sizeId)+str(pid)+str(message) 
            #Contador a ser passado para o HOP 
            contHop = len(connected_peers.items())-2
            lenHop = len(str(contHop))
            trueMessage = trueMessage + str(contHop) + str(lenHop) 
            hopMessage(connected_peers,trueMessage,destinatario)
            
            #Envia mensagem  
            threading.Thread(target=peer_connection, args=(realAddr, trueMessage)).start()
            IdEncontrado = True
            print("Mensagem enviada")
    #Caso nao tenha achado o ID retorna mensagem         
    if(IdEncontrado != True):
        print("ID não encontrado")            

if __name__ == "__main__":
    peer_id = str(uuid.uuid4())[:6]
    
    private_key,public_key = generate_keys()
    # private_key, public_key= generate_keys()
    save_public_key(public_key, peer_id)
    save_private_key(private_key, peer_id)
    connected_peers = peer(peer_id, public_key)
    print(
        f"Peer ID: {peer_id}\nPublic key{public_key}\nPrivate key{private_key}"
    )
    while True:
        message = input("> ")
        send_message(connected_peers, message)


#função encripta com chave publica de outros
#função decripta mensagem quando chega
#função encripta mensagem com chave de sessão
#Função gera chave de seção