import socket
import threading

peers = {}


def format_peers():
    peers_data = ";".join(
        [f"{pid},{info[0]},{info[1]}" for pid, info in peers.items()]
    )
    print(f"Peers data: {peers_data}")
    return peers_data


def notify_all_peers():
    global peers
    peer_list = format_peers()
    for peer_id, (peer_ip, peer_port) in peers.items():
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((peer_ip, peer_port))
            conn.sendall(f"PEER_LIST;{peer_list}".encode())
            conn.close()
        except Exception as e:
            print(f"Failed to notify peer {peer_id}: {e}")


def handle_peer(conn, addr):
    global peers
    try:
        peer_info = conn.recv(1024).decode()
        peer_id, peer_ip, peer_port = peer_info.split(",")
        peers[peer_id] = (peer_ip, int(peer_port))
        print(f"Peer {peer_id} connected from {addr}")

        # Notify all peers about the new list
        notify_all_peers()

    finally:
        conn.close()


def rendezvous_server(host="0.0.0.0", port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Rendezvous server listening on {host}:{port}")

    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_peer, args=(conn, addr)).start()
    except KeyboardInterrupt:
        server_socket.close()


if __name__ == "__main__":
    rendezvous_server()
