import socket
import threading

class P2PServer:
    def __init__(self):
        self.is_host = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.running = True
        
    def setup(self, ip="0.0.0.0", port=5555, target_ip=None):
        if self.is_host:
            # Host: Listen for connection
            self.sock.bind((ip, port))
            self.sock.listen(1)
            print(f"[HOST] Waiting for connection on {ip}:{port}...")
            self.conn, addr = self.sock.accept()
            print(f"[HOST] Connected with {addr}")
        else:
            # Client: Connect to host
            self.sock.connect((target_ip, port))
            self.conn = self.sock
            print(f"[CLIENT] Connected to {target_ip}:{port}")

        # Start receive thread
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def send(self, message):
        try:
            self.conn.sendall(message.encode('utf-8'))
        except:
            print("[ERROR] Failed to send message.")

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
        self.conn.close()
        self.sock.close()

# === Usage ===
def main():
    role = input("Are you host or client? (h/c): ").lower()

    if role == 'h':
        chat = P2PServer(is_host=True, port=5555)
    else:
        target_ip = input("Enter host IP: ")
        chat = P2PServer(is_host=False, port=5555, target_ip=target_ip)

    # Chat loop
    while chat.running:
        try:
            msg = input("> ")
            if msg.lower() == "exit":
                chat.close()
                break
            chat.send(msg)
        except KeyboardInterrupt:
            chat.close()
            break

if __name__ == "__main__":
    main()
