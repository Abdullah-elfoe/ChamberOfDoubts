import socket
import threading

class P2PNode:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.running = True

    def start_server(self, ip="0.0.0.0", port=5555):
        # Start listening in a new thread
        self.sock.bind((ip, port))
        self.sock.listen(1)
        print(f"[P2PNode] Listening for incoming connections on {ip}:{port}...")
        threading.Thread(target=self._accept_connection, daemon=True).start()

    def _accept_connection(self):
        self.conn, addr = self.sock.accept()
        print(f"[P2PNode] Incoming connection from {addr}")
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def connect_to_peer(self, target_ip, port=5555):
        # Outgoing connection (client role)
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.connect((target_ip, port))
            self.conn = client_sock
            print(f"[P2PNode] Connected to peer at {target_ip}:{port}")
            threading.Thread(target=self.receive_loop, daemon=True).start()
        except Exception as e:
            print(f"[ERROR] Failed to connect to peer: {e}")

    def send(self, message):
        if self.conn:
            try:
                self.conn.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"[ERROR] Failed to send message: {e}")
        else:
            print("[WARN] No connection established yet.")

    def receive_loop(self):
        while self.running:
            try:
                data = self.conn.recv(1024)
                if not data:
                    break
                print(f"\n[RECEIVED] {data.decode('utf-8')}\n> ", end="")
            except:
                break
        print("[INFO] Connection closed.")
        self.running = False

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()
        self.sock.close()

# === Usage ===
def main():
    node = P2PNode()
    port = 5555

    # Always start server to accept connections (P2P behavior)
    node.start_server(port=port)

    # Optionally connect to a peer
    choice = input("Do you want to connect to a peer? (y/n): ").lower()
    if choice == 'y':
        target_ip = input("Enter peer IP: ")
        node.connect_to_peer(target_ip, port=port)

    # Chat loop
    while node.running:
        try:
            msg = input("> ")
            if msg.lower() == "exit":
                node.close()
                break
            node.send(msg)
        except KeyboardInterrupt:
            node.close()
            break

if __name__ == "__main__":
    main()
