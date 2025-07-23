import socket
import threading
import json
import queue

class P2PNetwork:
    def __init__(self, port=5000):
        self.port = port
        self.listener_thread = None
        self.connection_thread = None
        self.server_socket = None
        self.client_socket = None
        self.connected = False
        self.running = False
        self.message_queue = queue.Queue()  # To hold received messages

    def start_listening(self):
        if self.running:
            return
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_thread, daemon=True)
        self.listener_thread.start()

    def stop_listening(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.server_socket = None

    def _listen_thread(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(1.0)

        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                self.client_socket = conn
                self.connected = True
                self._start_receiver_thread()
                print(f"[P2P] Connected to peer at {addr}")
                break
            except socket.timeout:
                continue
            except Exception as e:
                print("[P2P] Listener error:", e)
                break

    def connect(self, ip, port):
        def connect_thread():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, port))
                self.client_socket = sock
                self.connected = True
                self._start_receiver_thread()
                print(f"[P2P] Connected to peer at {ip}:{port}")
            except Exception as e:
                print(f"[P2P] Failed to connect: {e}")

        self.connection_thread = threading.Thread(target=connect_thread, daemon=True)
        self.connection_thread.start()

    def _start_receiver_thread(self):
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _receive_loop(self):
        while self.connected and self.client_socket:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    print("[P2P] Peer disconnected")
                    self.connected = False
                    break

                try:
                    decoded = data.decode()
                    if decoded.startswith("{") and decoded.endswith("}"):
                        self.message_queue.put(("json", json.loads(decoded)))
                    else:
                        self.message_queue.put(("chat", decoded))
                except Exception as e:
                    print("[P2P] Failed to parse incoming message:", e)

            except Exception as e:
                print("[P2P] Receive error:", e)
                self.connected = False
                break

    def send_chat(self, text):
        if self.connected and self.client_socket:
            try:
                self.client_socket.sendall(text.encode())
            except:
                self.connected = False

    def send_game(self, data_dict):
        try:
            json_str = json.dumps(data_dict)
            self.send_chat(json_str)
        except Exception as e:
            print("[P2P] Failed to send game data:", e)

    def update(self):
        """Call this in your main loop to process received messages."""
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        return messages

    @property
    def is_connected(self):
        return self.connected
