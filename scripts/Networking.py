# import socket
# import threading
# import json
# import queue
# import time
# import struct  # For message framing

# class P2PNetwork:
#     def __init__(self, port=5000):
#         print(f"[P2P-INIT] Initializing P2PNetwork on port {port}")
#         self.port = port
#         self.listener_thread = None
#         self.connection_thread = None
#         self.server_socket = None
#         self.client_socket = None
#         self.connected = False
#         self.running = False
#         self.message_queue = queue.Queue()
#         self.reconnect_attempt_delay = 5
#         self.peerIp = None
#         self.peerPort = None

#         self.send_ready = threading.Event()
#         self._send_lock = threading.Lock()
#         print("[P2P-INIT] send_ready event created (initially clear).")

#     def start_listening(self):
#         print("[P2P-LISTENER] Attempting to start listener...")
#         if self.running:
#             print("[P2P-LISTENER] Listener already running, aborting start.")
#             return
#         self.running = True
#         self.listener_thread = threading.Thread(target=self._listen_thread, daemon=True)
#         self.listener_thread.start()
#         print(f"[P2P-LISTENER] Listener thread started for port {self.port}.")

#     def stop_listening(self):
#         print("[P2P-LISTENER] Attempting to stop listener...")
#         if not self.running:
#             print("[P2P-LISTENER] Listener not running, aborting stop.")
#             return
#         print("[P2P-LISTENER] Setting self.running to False.")
#         self.running = False
#         if self.server_socket:
#             print("[P2P-LISTENER] Shutting down server socket.")
#             try:
#                 self.server_socket.shutdown(socket.SHUT_RDWR)
#                 self.server_socket.close()
#             except OSError as e:
#                 print(f"[P2P-LISTENER-ERROR] Error closing server socket: {e}")
#             self.server_socket = None
#         self.disconnect() # Ensure client socket is also closed cleanly
#         print("[P2P-LISTENER] Stop listening process completed.")

#     def _listen_thread(self):
#         print("[P2P-LISTEN-THREAD] Listener thread started running.")
#         ports_to_try = [self.port, 6000, 7000]
#         bound_successfully = False

#         for p in ports_to_try:
#             print(f"[P2P-LISTEN-THREAD] Trying to bind to port {p}...")
#             self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#             try:
#                 self.server_socket.bind(("", p))
#                 self.server_socket.listen(1)
#                 self.server_socket.settimeout(1.0)
#                 self.port = p # Update the class's port
#                 print(f"[P2P-LISTEN-THREAD] Successfully bound to port {self.port}. Listening...")
#                 bound_successfully = True
#                 break
#             except OSError as e:
#                 print(f"[P2P-LISTEN-THREAD-ERROR] Failed to bind or listen on port {p}: {e}")
#                 if self.server_socket:
#                     self.server_socket.close()
#                 self.server_socket = None

#         if not bound_successfully:
#             print("[P2P-LISTEN-THREAD-FATAL] Could not bind to any available port. Listener failed to start.")
#             self.running = False
#             return

#         print("[P2P-LISTEN-THREAD] Entering main accept loop.")
#         while self.running:
#             if self.connected:
#                 # print("[P2P-LISTEN-THREAD] Already connected, sleeping briefly.") # Too verbose, uncomment if needed
#                 time.sleep(0.1)
#                 continue
#             try:
#                 print("[P2P-LISTEN-THREAD] Waiting for incoming connection (accepting)...")
#                 conn, addr = self.server_socket.accept()
#                 if self.connected:
#                     print(f"[P2P-LISTEN-THREAD] Race condition: Already connected, closing new connection from {addr}.")
#                     conn.close()
#                     continue
#                 self.client_socket = conn
#                 self.client_socket.settimeout(1.0)
#                 self.connected = True
#                 self.peerIp, self.peerPort = addr
#                 self.ip, _ = conn.getsockname()
#                 print(f"[P2P-LISTEN-THREAD] Incoming connection ESTABLISHED from {addr} (Local: {self.ip}:{self.port}).")
#                 self._start_receiver_thread()
#             except socket.timeout:
#                 # print("[P2P-LISTEN-THREAD] Accept timeout, retrying.") # Too verbose, uncomment if needed
#                 continue
#             except Exception as e:
#                 print(f"[P2P-LISTEN-THREAD-ERROR] Listener accept error: {e}. Stopping listener.")
#                 self.running = False
#                 break
#         print("[P2P-LISTEN-THREAD] Listener thread stopped gracefully.")

#     def connect(self, ip, port):
#         print(f"[P2P-CONNECT] Attempting to initiate connection to {ip}:{port}...")
#         def connect_thread_func():
#             print("[P2P-CONNECT-THREAD] Connection thread started.")
#             if self.connected:
#                 print("[P2P-CONNECT-THREAD] Already connected, not attempting new outgoing connection.")
#                 return
#             try:
#                 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 sock.settimeout(5) # Timeout for the connect() call itself
#                 print(f"[P2P-CONNECT-THREAD] Connecting to {ip}:{port}...")
#                 sock.connect((ip, port))
#                 self.client_socket = sock
#                 self.client_socket.settimeout(1.0) # Timeout for receiving on client socket
#                 self.connected = True
#                 self.peerIp, self.peerPort = sock.getpeername()
#                 self.ip, self.port = sock.getsockname() # Update local IP and port from the client side connection
#                 print(f"[P2P-CONNECT-THREAD] Outgoing connection ESTABLISHED to {ip}:{port} (Local: {self.ip}:{self.port}).")
#                 self._start_receiver_thread()
#             except Exception as e:
#                 print(f"[P2P-CONNECT-THREAD-ERROR] Failed to connect to {ip}:{port} - {e}. Disconnecting.")
#                 self.disconnect()

#         if self.connection_thread and self.connection_thread.is_alive():
#             print("[P2P-CONNECT] Connection attempt already in progress, aborting new attempt.")
#             return

#         self.connection_thread = threading.Thread(target=connect_thread_func, daemon=True)
#         self.connection_thread.start()
#         print("[P2P-CONNECT] Connection thread initiated.")

#     def _start_receiver_thread(self):
#         print("[P2P-RECEIVER] Attempting to start receiver thread.")
#         if hasattr(self, '_receiver_thread') and self._receiver_thread and self._receiver_thread.is_alive():
#             print("[P2P-RECEIVER] Receiver thread already running for current connection, aborting new start.")
#             return

#         print("[P2P-RECEIVER] Clearing send_ready event.")
#         self.send_ready.clear()  # Block sending until we're ready
#         self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
#         self._receiver_thread.start()
        
#         # This thread sets send_ready after a short delay
#         threading.Thread(target=self._enable_send_after_delay, daemon=True).start()
#         print("[P2P-RECEIVER] Receiver thread and send_ready enablement thread initiated.")

#     def _enable_send_after_delay(self, delay=0.5):
#         print(f"[P2P-SEND-READY] _enable_send_after_delay called. Sleeping for {delay} seconds...")
#         time.sleep(delay)
#         self.send_ready.set()
#         print("[P2P-SEND-READY] send_ready event SET. Sending is now enabled.")

#     def _receive_loop(self):
#         print("[P2P-RECEIVER-LOOP] Receiver loop started.")
#         buffer = b""
#         MESSAGE_LENGTH_FIELD_SIZE = 4

#         while self.connected and self.client_socket:
#             try:
#                 # print("[P2P-RECEIVER-LOOP] Waiting to receive data...") # Too verbose, uncomment if needed
#                 data = self.client_socket.recv(4096)
#                 if not data:
#                     print("[P2P-RECEIVER-LOOP] Peer disconnected gracefully (recv returned no data).")
#                     self.disconnect()
#                     break
                
#                 # print(f"[P2P-RECEIVER-LOOP] Received {len(data)} bytes into buffer.")
#                 buffer += data

#                 while len(buffer) >= MESSAGE_LENGTH_FIELD_SIZE:
#                     # print(f"[P2P-RECEIVER-LOOP] Buffer has at least length field. Current buffer size: {len(buffer)}")
#                     message_length = struct.unpack("!I", buffer[:MESSAGE_LENGTH_FIELD_SIZE])[0]
                    
#                     if len(buffer) >= MESSAGE_LENGTH_FIELD_SIZE + message_length:
#                         full_message_bytes = buffer[MESSAGE_LENGTH_FIELD_SIZE : MESSAGE_LENGTH_FIELD_SIZE + message_length]
#                         buffer = buffer[MESSAGE_LENGTH_FIELD_SIZE + message_length:]
                        
#                         try:
#                             decoded = full_message_bytes.decode("utf-8", errors="replace")
#                             # print(f"[P2P-RECEIVER-LOOP] Decoded message: {decoded[:100]}...")
#                             if decoded.startswith("{") and decoded.endswith("}"):
#                                 try:
#                                     json_data = json.loads(decoded)
#                                     self.message_queue.put(("json", json_data))
#                                     print("[P2P-RECEIVER-LOOP] JSON message put on queue.")
#                                 except json.JSONDecodeError:
#                                     print(f"[P2P-RECEIVER-LOOP-ERROR] Invalid JSON received: {decoded[:100]}... (treating as chat)")
#                                     self.message_queue.put(("chat", decoded.strip()))
#                             else:
#                                 self.message_queue.put(("chat", decoded.strip()))
#                                 print("[P2P-RECEIVER-LOOP] Chat message put on queue.")
#                         except UnicodeDecodeError as e:
#                             print(f"[P2P-RECEIVER-LOOP-ERROR] Unicode decode error on message: {e}")
#                         except Exception as e:
#                             print(f"[P2P-RECEIVER-LOOP-ERROR] Error processing decoded message: {e}")
#                     else:
#                         # print(f"[P2P-RECEIVER-LOOP] Not enough data for full message (need {message_length + MESSAGE_LENGTH_FIELD_SIZE}, got {len(buffer)}). Waiting for more.")
#                         break # Not enough data for current message, wait for more

#             except socket.timeout:
#                 # print("[P2P-RECEIVER-LOOP] Socket recv timeout, continuing loop.") # Too verbose
#                 continue
#             except (ConnectionResetError, BrokenPipeError):
#                 print("[P2P-RECEIVER-LOOP-ERROR] Peer disconnected (connection error).")
#                 self.disconnect()
#                 break
#             except OSError as e:
#                 print(f"[P2P-RECEIVER-LOOP-ERROR] Socket error: {e}. Disconnecting.")
#                 self.disconnect()
#                 break
#             except Exception as e:
#                 print(f"[P2P-RECEIVER-LOOP-ERROR] Unknown error in receive loop: {e}. Disconnecting.")
#                 self.disconnect()
#                 break
#         print("[P2P-RECEIVER-LOOP] Receiver loop stopped.")

#     def send_chat(self, text):
#         print(f"[P2P-SEND-CHAT] send_chat called with text: {text[:50]}...")
#         if not self.send_ready.is_set():
#             print("[P2P-SEND-CHAT] send_ready is NOT set. Waiting for connection to stabilize (max 3s)...")
#             if not self.send_ready.wait(timeout=3.0):
#                 print("[P2P-SEND-CHAT-ABORT] Timeout: Connection not ready for sending chat. Aborting send.")
#                 return
#             else:
#                 print("[P2P-SEND-CHAT] send_ready is now SET after waiting.")

#         if not self.connected or not self.client_socket:
#             print("[P2P-SEND-CHAT-ABORT] Not connected or client_socket is invalid. Cannot send chat.")
#             return

#         with self._send_lock:
#             try:
#                 message_bytes = text.encode("utf-8")
#                 length_prefix = struct.pack("!I", len(message_bytes))
                
#                 print(f"[P2P-SEND-CHAT] Attempting to send {len(message_bytes)} bytes (with {len(length_prefix)} byte prefix)...")
#                 self.client_socket.sendall(length_prefix + message_bytes)
#                 print("[P2P-SEND-CHAT] Data sent successfully.")
#             except (BrokenPipeError, ConnectionResetError, OSError) as e:
#                 print(f"[P2P-SEND-CHAT-ERROR] Send error (connection lost/timeout) for chat: {e}. Disconnecting.")
#                 self.disconnect()
#             except Exception as e:
#                 print(f"[P2P-SEND-CHAT-ERROR] Unexpected send error for chat: {e}. Disconnecting.")
#                 self.disconnect()

#     def send_game(self, data_dict):
#         print(f"[P2P-SEND-GAME] send_game called with data: {str(data_dict)[:100]}...")
#         # send_game calls send_chat, which already has the send_ready check and prints.
#         # No need to duplicate the check here, but the initial print is useful.
#         try:
#             json_str = json.dumps(data_dict)
#             print(f"[P2P-SEND-GAME] Converted data to JSON string. Calling send_chat...")
#             self.send_chat(json_str)
#         except TypeError as e:
#             print(f"[P2P-SEND-GAME-ERROR] Failed to serialize game data (TypeError): {e}")
#         except Exception as e:
#             print(f"[P2P-SEND-GAME-ERROR] Unexpected error preparing game data: {e}")

#     def update(self):
#         messages = []
#         while not self.message_queue.empty():
#             messages.append(self.message_queue.get())
#         return messages

#     def disconnect(self):
#         print("[P2P-DISCONNECT] Disconnect method called.")
#         if not self.connected:
#             print("[P2P-DISCONNECT] Not currently connected, aborting disconnect.")
#             return
        
#         print("[P2P-DISCONNECT] Setting self.connected to False.")
#         self.connected = False
#         print("[P2P-DISCONNECT] Clearing send_ready event.")
#         self.send_ready.clear() # Clear event on disconnect

#         if self.client_socket:
#             print("[P2P-DISCONNECT] Attempting to shutdown and close client socket.")
#             try:
#                 self.client_socket.shutdown(socket.SHUT_RDWR)
#                 self.client_socket.close()
#             except OSError as e:
#                 print(f"[P2P-DISCONNECT-ERROR] Error closing client socket: {e}")
#             self.client_socket = None
        
#         # Clear any pending messages in the queue
#         print("[P2P-DISCONNECT] Clearing message queue.")
#         while not self.message_queue.empty():
#             try:
#                 self.message_queue.get_nowait()
#             except queue.Empty:
#                 break
#         print("[P2P-DISCONNECT] Disconnection process completed.")

#     @property
#     def is_connected(self):
#         return self.connected


import socket
import json
import threading
import time
import queue
import struct
import logging
from typing import Dict, Any, Callable, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class P2PNetwork:
    """
    High-performance thread-safe P2P networking class for pygame applications.
    Supports true concurrent chat and game data transmission without blocking.
    
    Features:
    - Non-blocking concurrent message sending
    - Separate acknowledgment handling
    - Optimized for high-frequency game updates
    - Thread-safe operations
    """
    
    # Message types
    MSG_CHAT = 1
    MSG_GAME = 2
    MSG_ACK = 3
    MSG_HEARTBEAT = 4
    
    def __init__(self, ip: str="192.168.0.102", port: int=5000, peer_ip: str="192.168.0.108", peer_port: int=6000):
        """
        Initialize P2P network for pygame.
        
        Args:
            ip: Local IP address (self.ip)
            port: Local port number (self.port)
            peer_ip: Peer IP address (self.peerIp)
            peer_port: Peer port number (self.peerPort)
        """
        # Required attributes as specified
        self.ip = ip
        self.port = port
        self.peerIp = peer_ip
        self.peerPort = peer_port
        
        # Internal networking state
        self._lock = threading.RLock()
        self._running = False
        self._connected = False
        
        # Socket management
        self._server_socket = None
        self._client_socket = None
        self._peer_socket = None
        
        # Threading
        self._server_thread = None
        self._client_thread = None
        self._receive_thread = None
        self._send_thread = None
        self._heartbeat_thread = None
        self._ack_thread = None
        
        # Message queues for thread-safe communication
        self._send_queue = queue.Queue()
        self._received_messages = queue.Queue()
        
        # Non-blocking acknowledgment system
        self._message_counter = 0
        self._pending_acks = {}
        self._ack_timeout = 2.0  # Reduced timeout for faster processing
        self._max_retries = 2    # Reduced retries for faster processing
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'chat_sent': 0,
            'chat_received': 0,
            'game_sent': 0,
            'game_received': 0,
            'errors': 0,
            'retries': 0
        }
        
        # Performance optimization
        self._send_buffer = []
        self._last_flush = time.time()
        self._flush_interval = 0.016  # ~60 FPS for game data
        
        logger.info(f"P2P Network initialized: {self.ip}:{self.port} <-> {self.peerIp}:{self.peerPort}")
    
    def start_listening(self):
        """Start listening for P2P connections (server mode)."""
        with self._lock:
            if self._running:
                logger.warning("P2P network is already running")
                return False
            
            self._running = True
            logger.info(f"Starting P2P listener on {self.ip}:{self.port}")
            
            # Start server thread (listen for incoming connections)
            self._server_thread = threading.Thread(target=self._server_worker, daemon=True)
            self._server_thread.start()
            
            # Start heartbeat thread
            self._heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
            self._heartbeat_thread.start()
            
            # Start ACK management thread
            self._ack_thread = threading.Thread(target=self._ack_worker, daemon=True)
            self._ack_thread.start()
            
            return True
    
    def stop_listening(self):
        """Stop listening for P2P connections."""
        with self._lock:
            if not self._running:
                return
            
            logger.info("Stopping P2P network")
            self._running = False
            self._connected = False
            
            # Close all sockets
            self._close_sockets()
            
            # Clear queues
            self._clear_queues()
    
    def connect(self, peer_ip: str, peer_port: int):
        """
        Connect to a specific peer.
        
        Args:
            peer_ip: IP address of the peer to connect to
            peer_port: Port number of the peer to connect to
        
        Returns:
            bool: True if connection attempt started, False otherwise
        """
        if not self._running:
            logger.error("Must start listening before connecting to peers")
            return False
        
        if self._connected:
            logger.warning("Already connected to a peer")
            return False
        
        # Update peer information
        self.peerIp = peer_ip
        self.peerPort = peer_port
        
        logger.info(f"Initiating connection to {peer_ip}:{peer_port}")
        
        # Start client thread to connect to specific peer
        self._client_thread = threading.Thread(target=self._client_worker, daemon=True)
        self._client_thread.start()
        
        return True
    
    def send_chat(self, message: str):
        """
        Send a chat message to the peer (non-blocking).
        
        Args:
            message: Chat message string (e.g., "hi", "hello bro")
        
        Returns:
            bool: True if message was queued successfully, False otherwise
        """
        if not isinstance(message, str):
            logger.error("Chat message must be a string")
            return False
        
        if not message.strip():
            logger.error("Chat message cannot be empty")
            return False
        
        if not self._connected:
            logger.warning("Cannot send chat - not connected to peer")
            return False
        
        try:
            self._queue_message(self.MSG_CHAT, message.strip())
            self.stats['chat_sent'] += 1
            logger.debug(f"Queued chat message: '{message.strip()}'")
            return True
        except Exception as e:
            logger.error(f"Failed to queue chat message: {e}")
            self.stats['errors'] += 1
            return False
    
    def send_game(self, data: Dict[str, Any]):
        """
        Send game data to the peer (non-blocking, optimized for high frequency).
        
        Args:
            data: Game data dictionary that will be converted to JSON
        
        Returns:
            bool: True if data was queued successfully, False otherwise
        """
        if not isinstance(data, dict):
            logger.error("Game data must be a dictionary")
            return False
        
        if not self._connected:
            logger.warning("Cannot send game data - not connected to peer")
            return False
        # print(data, type(data))
        
        try:
            # Convert dictionary to JSON string
            json_data = json.dumps(data, separators=(',', ':'))
            self._queue_message(self.MSG_GAME, json_data)
            self.stats['game_sent'] += 1
            logger.debug(f"Queued game data: {data}")
            return True
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize game data: {e}")
            self.stats['errors'] += 1
            print("unsuccessful", e)
            return False
        except Exception as e:
            logger.error(f"Failed to queue game data: {e}")
            self.stats['errors'] += 1
            return False
    
    def get_received_messages(self):
        """
        Get all received messages since last call.
        
        Returns:
            list: List of received message dictionaries with format:
                  {'type': 'chat'/'game', 'content': str/dict, 'timestamp': float}
        """
        messages = []
        try:
            while not self._received_messages.empty():
                messages.append(self._received_messages.get_nowait())
        except queue.Empty:
            pass
        return messages
    
    def is_connected(self) -> bool:
        """Check if connected to peer."""
        return self._connected
    
    def is_running(self) -> bool:
        """Check if P2P network is running."""
        return self._running
    
    def get_stats(self) -> Dict[str, int]:
        """Get connection statistics."""
        return self.stats.copy()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            'local_ip': self.ip,
            'local_port': self.port,
            'peer_ip': self.peerIp,
            'peer_port': self.peerPort,
            'connected': self._connected,
            'running': self._running
        }
    
    # Internal methods
    def _queue_message(self, msg_type: int, payload: str):
        """Queue a message for sending (non-blocking)."""
        with self._lock:
            self._message_counter += 1
            message = {
                'id': self._message_counter,
                'type': msg_type,
                'payload': payload,
                'timestamp': time.time(),
                'retries': 0
            }
            
            # For game messages, use immediate sending for better performance
            if msg_type == self.MSG_GAME:
                self._send_queue.put(message)
            else:
                # For chat and other messages, queue normally
                self._send_queue.put(message)
    
    def _server_worker(self):
        """Server thread worker to accept incoming connections."""
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.ip, self.port))
            self._server_socket.listen(1)
            self._server_socket.settimeout(1.0)
            
            logger.info(f"Server listening on {self.ip}:{self.port}")
            
            while self._running:
                try:
                    peer_socket, peer_addr = self._server_socket.accept()
                    logger.info(f"Accepted connection from {peer_addr}")
                    
                    if not self._connected:
                        self._establish_connection(peer_socket)
                    else:
                        peer_socket.close()
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        logger.error(f"Server error: {e}")
                        self.stats['errors'] += 1
                        time.sleep(1)
                        
        except Exception as e:
            logger.error(f"Server setup error: {e}")
            self.stats['errors'] += 1
    
    def _client_worker(self):
        """Client thread worker to connect to peer."""
        retry_delay = 1.0
        max_retry_delay = 5.0  # Reduced max delay for faster reconnection
        
        while self._running and not self._connected:
            try:
                logger.info(f"Attempting to connect to {self.peerIp}:{self.peerPort}")
                
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(3.0)  # Reduced timeout
                client_socket.connect((self.peerIp, self.peerPort))
                
                logger.info(f"Connected to peer at {self.peerIp}:{self.peerPort}")
                self._establish_connection(client_socket)
                break
                
            except Exception as e:
                if self._running:
                    logger.warning(f"Connection attempt failed: {e}")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, max_retry_delay)
    
    def _establish_connection(self, peer_socket: socket.socket):
        """Establish connection with peer socket."""
        with self._lock:
            if self._connected:
                peer_socket.close()
                return
            
            self._peer_socket = peer_socket
            self._peer_socket.settimeout(None)
            # Enable TCP_NODELAY for lower latency
            self._peer_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._connected = True
            
            # Start communication threads
            self._receive_thread = threading.Thread(target=self._receive_worker, daemon=True)
            self._receive_thread.start()
            
            self._send_thread = threading.Thread(target=self._send_worker, daemon=True)
            self._send_thread.start()
            
            logger.info("P2P connection established successfully")
    
    def _send_worker(self):
        """High-performance worker thread to send queued messages."""
        while self._running and self._connected:
            try:
                messages_to_send = []
                
                # Collect multiple messages for batch sending
                try:
                    # Get first message (blocking with timeout)
                    message = self._send_queue.get(timeout=0.1)
                    messages_to_send.append(message)
                    
                    # Collect additional messages if available (non-blocking)
                    while len(messages_to_send) < 10:  # Limit batch size
                        try:
                            message = self._send_queue.get_nowait()
                            messages_to_send.append(message)
                        except queue.Empty:
                            break
                            
                except queue.Empty:
                    continue
                
                # Send all messages in batch
                for message in messages_to_send:
                    if self._send_message_immediate(message):
                        self.stats['messages_sent'] += 1
                    else:
                        # Retry failed messages
                        if message['retries'] < self._max_retries:
                            message['retries'] += 1
                            self._send_queue.put(message)
                            self.stats['retries'] += 1
                        else:
                            logger.warning(f"Message {message['id']} failed after {self._max_retries} retries")
                            self.stats['errors'] += 1
                    
                    # Mark task as done
                    self._send_queue.task_done()
                
            except Exception as e:
                logger.error(f"Send worker error: {e}")
                self.stats['errors'] += 1
                time.sleep(0.01)
    
    def _send_message_immediate(self, message: Dict) -> bool:
        """Send message immediately without waiting for ACK (for performance)."""
        try:
            if not self._connected:
                return False
            
            # Prepare message data
            msg_data = {
                'id': message['id'],
                'type': message['type'],
                'payload': message['payload'],
                'timestamp': message['timestamp']
            }
            
            # Serialize and send
            serialized = json.dumps(msg_data).encode('utf-8')
            length = struct.pack('!I', len(serialized))
            
            with self._lock:
                if self._peer_socket:
                    self._peer_socket.sendall(length + serialized)
                    
                    # For non-heartbeat messages, track for ACK but don't wait
                    if message['type'] != self.MSG_HEARTBEAT:
                        self._pending_acks[message['id']] = time.time()
                    
                    return True
            
        except Exception as e:
            logger.debug(f"Send failed: {e}")
            return False
        
        return False
    
    def _receive_worker(self):
        """High-performance worker thread to receive messages from peer."""
        buffer = b''
        
        while self._running and self._connected:
            try:
                if not self._peer_socket:
                    break
                
                # Receive data with larger buffer for better performance
                data = self._peer_socket.recv(8192)
                if not data:
                    logger.info("Peer disconnected")
                    break
                
                buffer += data
                
                # Process complete messages
                while len(buffer) >= 4:
                    # Get message length
                    msg_length = struct.unpack('!I', buffer[:4])[0]
                    
                    if len(buffer) < 4 + msg_length:
                        break
                    
                    # Extract message
                    msg_data = buffer[4:4 + msg_length]
                    buffer = buffer[4 + msg_length:]
                    
                    # Process message in separate thread for better performance
                    threading.Thread(target=self._process_received_message, 
                                   args=(msg_data,), daemon=True).start()
                
            except Exception as e:
                if self._running and self._connected:
                    logger.error(f"Receive error: {e}")
                    self.stats['errors'] += 1
                break
        
        # Connection lost
        self._handle_disconnection()
    
    def _process_received_message(self, msg_data: bytes):
        """Process a received message (runs in separate thread for performance)."""
        try:
            message = json.loads(msg_data.decode('utf-8'))
            msg_id = message.get('id')
            msg_type = message.get('type')
            payload = message.get('payload')
            
            # Send ACK for non-heartbeat messages (non-blocking)
            if msg_type != self.MSG_HEARTBEAT and msg_type != self.MSG_ACK:
                threading.Thread(target=self._send_ack, args=(msg_id,), daemon=True).start()
            
            # Handle different message types
            if msg_type == self.MSG_CHAT:
                logger.debug(f"Received chat: '{payload}'")
                self.stats['messages_received'] += 1
                self.stats['chat_received'] += 1
                self._received_messages.put({
                    'type': 'chat',
                    'content': payload,
                    'timestamp': time.time()
                })
                    
            elif msg_type == self.MSG_GAME:
                try:
                    game_data = json.loads(payload)
                    logger.debug(f"Received game data: {game_data}")
                    self.stats['messages_received'] += 1
                    self.stats['game_received'] += 1
                    self._received_messages.put({
                        'type': 'game',
                        'content': game_data,
                        'timestamp': time.time()
                    })
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse game data: {e}")
                    
            elif msg_type == self.MSG_ACK:
                # Remove from pending ACKs
                try:
                    ack_id = int(payload)
                    self._pending_acks.pop(ack_id, None)
                except (ValueError, KeyError):
                    pass
                
            elif msg_type == self.MSG_HEARTBEAT:
                logger.debug("Received heartbeat")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.stats['errors'] += 1
    
    def _send_ack(self, msg_id: int):
        """Send acknowledgment for received message (non-blocking)."""
        try:
            ack_data = {
                'id': 0,  # ACKs don't need IDs
                'type': self.MSG_ACK,
                'payload': str(msg_id),
                'timestamp': time.time()
            }
            
            serialized = json.dumps(ack_data).encode('utf-8')
            length = struct.pack('!I', len(serialized))
            
            with self._lock:
                if self._peer_socket:
                    self._peer_socket.sendall(length + serialized)
                    
        except Exception as e:
            logger.debug(f"Failed to send ACK: {e}")
    
    def _ack_worker(self):
        """Background thread to clean up old pending ACKs."""
        while self._running:
            try:
                current_time = time.time()
                with self._lock:
                    expired_acks = [
                        msg_id for msg_id, timestamp in self._pending_acks.items()
                        if current_time - timestamp > self._ack_timeout
                    ]
                    
                    for msg_id in expired_acks:
                        self._pending_acks.pop(msg_id, None)
                
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"ACK worker error: {e}")
                time.sleep(1.0)
    
    def _heartbeat_worker(self):
        """Send periodic heartbeat messages."""
        while self._running:
            time.sleep(5)  # Reduced heartbeat interval
            if self._connected:
                try:
                    self._queue_message(self.MSG_HEARTBEAT, "ping")
                except Exception as e:
                    logger.error(f"Failed to send heartbeat: {e}")
    
    def _handle_disconnection(self):
        """Handle peer disconnection."""
        with self._lock:
            if self._connected:
                self._connected = False
                logger.info("Peer disconnected")
    
    def _close_sockets(self):
        """Close all sockets."""
        try:
            if self._peer_socket:
                self._peer_socket.close()
                self._peer_socket = None
        except:
            pass
        
        try:
            if self._server_socket:
                self._server_socket.close()
                self._server_socket = None
        except:
            pass
        
        try:
            if self._client_socket:
                self._client_socket.close()
                self._client_socket = None
        except:
            pass
    
    def _clear_queues(self):
        """Clear all message queues."""
        try:
            while not self._send_queue.empty():
                self._send_queue.get_nowait()
        except:
            pass
        
        try:
            while not self._received_messages.empty():
                self._received_messages.get_nowait()
        except:
            pass


# Example usage for pygame integration
if __name__ == "__main__":
    # Example: Create two P2P instances for testing
    print("High-Performance P2P Network Class for Pygame")
    print("=" * 50)
    
    # Create P2P instance
    p2p = P2PNetwork("127.0.0.1", 8001, "127.0.0.1", 8002)
    
    # Start listening and connect
    print("Starting listener...")
    p2p.start_listening()
    
    print("Connecting to peer...")
    p2p.connect("127.0.0.1", 8002)
    
    # Wait for connection
    print("Waiting for connection...")
    time.sleep(3)
    
    if p2p.is_connected():
        print("Connected! Testing high-frequency messaging...")
        
        # Send rapid game updates (like your automation test)
        for i in range(100):
            # Send chat message
            p2p.send_chat(f"Rapid message {i}")
            
            # Send game data
            game_data = {
                "action": "move",
                "frame": i,
                "x": 100 + i,
                "y": 200 + i,
                "timestamp": time.time()
            }
            p2p.send_game(game_data)
            
            # Small delay to simulate game loop
            time.sleep(0.016)  # ~60 FPS
        
        # Check stats
        time.sleep(2)
        stats = p2p.get_stats()
        print(f"Messages sent: {stats['messages_sent']}")
        print(f"Errors: {stats['errors']}")
    else:
        print("Failed to connect to peer")
    
    # Stop listening
    time.sleep(2)
    p2p.stop_listening()
    print("High-frequency test completed.")