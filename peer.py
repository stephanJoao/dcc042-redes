import socket
import threading
import uuid
import random
from encryptionRSA import *
from encryptionAES import *
from sympy import public
import os
import time

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
        for key in connected_peers.keys():
            if not arrayList.__contains__(key):
                arrayList[key] = []
            else:
                arrayList[key] = arrayList[key]
        # handle_connection(conn, addr, peer_id, connected_peers,arrayList)
        threading.Thread(
            target=handle_connection,
            args=(conn, addr, peer_id, connected_peers,arrayList),
        ).start()


def handle_connection(conn, addr, peer_id, connected_peers, arrayList):
    try:
        message = conn.recv(1024).decode()

        if message.startswith("PEER_LIST;"):
            _, peers_data = message.split(";", 1)
            if peers_data:
                new_peers = parse_peers1(peers_data)
                arrayList = parse_peers2(peers_data,arrayList)
                connected_peers.clear()
                connected_peers.update(new_peers)
                print(f"Updated peers list: {connected_peers}")
        
        else:
            idMSGSize = int(message[0])
            idMSG = message[1:idMSGSize]
            auxMessage = message[idMSGSize:]
            sizeidpeer1= int(auxMessage[0])
            sizeidpeer2= int(auxMessage[sizeidpeer1:sizeidpeer1+1])
            sizeHops =int(auxMessage[-1])
            quantHops =int(auxMessage[-int(sizeHops)-1:-1])
            
            #Verifica se é apenas um Hop 
            if(quantHops>0):
                print(f"HOP -> {message}")
                message = message[:-int(sizeHops)-1]
                quantHops = quantHops - 1
                sizeHops = len(str(quantHops))
                message = message + str(quantHops) + str(sizeHops)
                if quantHops != 0:
                    hopMessage(connected_peers,message,str(auxMessage[1:sizeidpeer1]))
                else:
                    realAddr=tuple(connected_peers[auxMessage[1:sizeidpeer1]][:-1])
                    peer_connection(realAddr,message)
            else:
                if "SK:" in message:
                    data = message.split("SK:")
                    decryptMessage = data[1]
                    idSender = auxMessage[1+sizeidpeer1:sizeidpeer1+sizeidpeer2]
                    private_key = read_private_key(peer_id)
                    encryptMsg = decryptMessage[:-int(sizeHops)-1]
                    trueMessage = decrypt_message(private_key, encryptMsg)
                    sessioKey = bytes.fromhex(trueMessage)
                    sKFrag = {"sessionkey": sessioKey, "idSender": idSender, "idMsg": idMSG, "frags":[]}
                    arrayList[idSender].append(sKFrag)
                else:
                    if str(auxMessage[1:sizeidpeer1]) == str(peer_id):
                        encryptMsg = auxMessage[sizeidpeer1+sizeidpeer2:-int(sizeHops)-1]
                       
                        idSender = auxMessage[1+sizeidpeer1:sizeidpeer1+sizeidpeer2]
                        idReceiver = auxMessage[1:sizeidpeer1]
                        count = 0
                        for eachDict in arrayList[idSender]:
                            if eachDict["idMsg"] == idMSG:   
                                break
                            count = count +1
                        sessioKey = arrayList[idSender][count]["sessionkey"]
                        encryptMsg = bytes.fromhex(encryptMsg)
                        encryptMsg=decrypt_message_aes(encryptMsg,sessioKey) #.encode(encoding="utf-8")
                        private_key = read_private_key(peer_id)
                        encryptMsg = decrypt_message(private_key, encryptMsg)

                        idFragSize = int(encryptMsg[0])
                        numOfFragsSize = int(encryptMsg[-1])
                        idFrag = int(encryptMsg[1:idFragSize])
                        numOfFrags = int(encryptMsg[-int(numOfFragsSize)-1:-1])
                        fragMessage = encryptMsg[idFragSize:-int(numOfFragsSize)-1]
                        fragment = {
                            'id': idFrag,
                            'fragment': str(fragMessage)
                        }
                        arrayList[idSender][count]["frags"].append(fragment)
                        if verify_fragments(arrayList[idSender][count]["frags"],numOfFrags):
                            fragmentList = organize_fragments(arrayList[idSender][count]["frags"])
                            trueFragMsg = []
                            for each in fragmentList:
                                trueFragMsg.append(each["fragment"])
                            complete_message = ''.join(trueFragMsg)
                            print(f"[chat]: mensagem recebida original-> {complete_message}")
                            arrayList[idSender].pop(count)
                        else:
                            print(f"Colecting fragments")
                    else:
                        print(f"[chat]: mensagemrecebida com criptografia-> {message}")
    finally:
        conn.close()


def parse_peers1(peers_data):
    peers = {}
    if peers_data:
        for peer_info in peers_data.split(";"):
            peer_id, peer_ip, peer_port, public_key = peer_info.split(",")
            peers[peer_id] = (peer_ip, int(peer_port), public_key)
    return peers

def parse_peers2(peers_data, arrayList):
    peers = {}
    if peers_data:
        for peer_info in peers_data.split(";"):
            peer_id, peer_ip, peer_port, public_key = peer_info.split(",")
            peers[peer_id] = []
        for key in arrayList.keys():
            peers[key] = arrayList[key]
    return peers


def peer(
    peer_id, public_key, rendezvous_host="127.0.0.1", rendezvous_port=12345
):
    peer_port = random.randint(10000, 60000)
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind(("0.0.0.0", peer_port))
    arrayList = {}
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
    connected_peers.update(parse_peers1(peers_data))
    arrayList.update(parse_peers2(peers_data,arrayList))
    print(f"Initial peers: {connected_peers}\n> ")

    rendezvous_socket.close()

    return connected_peers


def peer_connection(addr, message):
    
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect(addr)
        idMSGSize = int(message[0])
        sizeId = int(message[idMSGSize])        
        realAddr=tuple(connected_peers[message[idMSGSize+1:sizeId+idMSGSize]][:-1])
        peer_socket.sendto(message.encode(),realAddr)
        peer_socket.close()
    except Exception as e:
        print(f"Could not connect to peer at {addr}: {e}")
    


def hopMessage(connected_peers,trueMessage,destinatario):
    destinatoriohop = pick_random_key(connected_peers,destinatario)
    print(destinatoriohop)
    realAddr=tuple(connected_peers[destinatoriohop][:-1])
    peer_connection(realAddr,trueMessage)

def send_messageFrags(messages,sizeId,pid,peer_idSize,peer_id,contHop,lenHop,randPeerKey,session_key,msgID):
    time.sleep(3)
    for eachMessage in messages:
                auxMessage = eachMessage["idSize"]+eachMessage["id"] + eachMessage["fragment"]+eachMessage["numMaxOfFrags"]+eachMessage["sizeNumMaxOfFrags"]
                
                
                auxMessage = encrypt_message(randPeerKey,auxMessage)
                
                auxMessage = encrypt_message_aes(auxMessage,session_key)
                
                auxMessage = auxMessage.hex()
                

                trueauxMessage = str(len(msgID)+1)+str(msgID)+str(sizeId)+str(pid)+str(peer_idSize)+peer_id+str(auxMessage) 
                trueauxMessage = trueauxMessage + str(contHop) + str(lenHop)

                hopMessage(connected_peers,trueauxMessage,pid)

def send_message(connected_peers, message,peer_id):
    #Propriedade para verificar se ID foi encontrado
    IdEncontrado = False
    print("Para qual Peer Id deseja enviar a mensagem:")
    destinatario = input()
    peer_idSize = len(peer_id)+1
    msgID = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
    print(msgID)
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
 
            randPeerKey = read_public_key(pid)
            sizeId = len(pid)+1

            message1 = session_key.hex()
            message1 = encrypt_message(randPeerKey,message1)
            trueMessage = str(len(msgID)+1)+str(msgID)+str(sizeId)+str(pid)+str(peer_idSize)+peer_id+"SK:"+str(message1) + str(0) + str(1)
            peer_connection(realAddr,trueMessage)
            #separação
            messages = fragment_message(message)
            # print(messages)
            send_messageFrags(messages,sizeId,pid,peer_idSize,peer_id,contHop,lenHop,randPeerKey,session_key,msgID)
            
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