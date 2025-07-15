import socket
import threading

class P2PClient:
    def __init__(self, target_ip, port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((target_ip, port))
        print(f"[CLIENT] Connected to {target_ip}:{port}")

        threading.Thread(target=self.send_loop, daemon=True).start()
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def send_loop(self):
        while True:
            msg = input("[CLIENT] Type message: ")
            self.client.send(msg.encode())

    def receive_loop(self):
        while True:
            try:
                data = self.client.recv(1024).decode()
                if not data:
                    break
                print(f"[CLIENT RECEIVED] {data}")
            except:
                break
        self.client.close()
        print("[CLIENT] Connection closed.")
