import socket
import threading

class P2PServer:
    def __init__(self, port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('', port))
        self.server.listen(1)
        print(f"[SERVER] Waiting for connection on port {port}...")

        self.conn, self.addr = self.server.accept()
        print(f"[SERVER] Connected by {self.addr}")

        threading.Thread(target=self.receive_loop, daemon=True).start()
        threading.Thread(target=self.send_loop, daemon=True).start()

    def receive_loop(self):
        while True:
            try:
                data = self.conn.recv(1024).decode()
                if not data:
                    break
                print(f"[SERVER RECEIVED] {data}")
            except:
                break
        self.conn.close()
        print("[SERVER] Connection closed.")

    def send_loop(self):
        while True:
            msg = input("[SERVER] Type message: ")
            self.conn.send(msg.encode())
