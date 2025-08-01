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


class P2PNetworkPygame:
    """
    Thread-safe P2P networking class designed for pygame applications.
    Supports concurrent chat and game data transmission without packet collision.
    
    Features:
    - Bidirectional P2P communication
    - Message type differentiation (chat vs game data)
    - Automatic retry with acknowledgment system
    - Thread-safe concurrent operations
    - Easy pygame integration
    """
    
    # Message types
    MSG_CHAT = 1
    MSG_GAME = 2
    MSG_ACK = 3
    MSG_HEARTBEAT = 4
    
    def __init__(self, ip: str, port: int, peer_ip: str, peer_port: int):
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
        
        # Message queues for thread-safe communication
        self._send_queue = queue.Queue()
        self._received_messages = queue.Queue()
        
        # Reliability system
        self._message_counter = 0
        self._pending_acks = {}
        self._ack_timeout = 3.0
        self._max_retries = 3
        
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
        
        logger.info(f"P2P Network initialized: {self.ip}:{self.port} <-> {self.peerIp}:{self.peerPort}")
    
    def start_connection(self):
        """Start the P2P network connection."""
        with self._lock:
            if self._running:
                logger.warning("P2P network is already running")
                return False
            
            self._running = True
            logger.info(f"Starting P2P connection on {self.ip}:{self.port}")
            
            # Start server thread (listen for incoming connections)
            self._server_thread = threading.Thread(target=self._server_worker, daemon=True)
            self._server_thread.start()
            
            # Start client thread (connect to peer)
            self._client_thread = threading.Thread(target=self._client_worker, daemon=True)
            self._client_thread.start()
            
            # Start heartbeat thread
            self._heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
            self._heartbeat_thread.start()
            
            return True
    
    def stop_connection(self):
        """Stop the P2P network connection."""
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
    
    def send_chat(self, message: str):
        """
        Send a chat message to the peer.
        
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
            logger.info(f"Queued chat message: '{message.strip()}'")
            return True
        except Exception as e:
            logger.error(f"Failed to queue chat message: {e}")
            self.stats['errors'] += 1
            return False
    
    def send_game(self, data: Dict[str, Any]):
        """
        Send game data to the peer.
        
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
        
        try:
            # Convert dictionary to JSON string
            json_data = json.dumps(data, separators=(',', ':'))
            self._queue_message(self.MSG_GAME, json_data)
            self.stats['game_sent'] += 1
            logger.info(f"Queued game data: {data}")
            return True
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize game data: {e}")
            self.stats['errors'] += 1
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
        """Queue a message for sending."""
        with self._lock:
            self._message_counter += 1
            message = {
                'id': self._message_counter,
                'type': msg_type,
                'payload': payload,
                'timestamp': time.time(),
                'retries': 0
            }
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
        max_retry_delay = 10.0
        
        while self._running and not self._connected:
            try:
                logger.info(f"Attempting to connect to {self.peerIp}:{self.peerPort}")
                
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(5.0)
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
            self._connected = True
            
            # Start communication threads
            self._receive_thread = threading.Thread(target=self._receive_worker, daemon=True)
            self._receive_thread.start()
            
            self._send_thread = threading.Thread(target=self._send_worker, daemon=True)
            self._send_thread.start()
            
            logger.info("P2P connection established successfully")
    
    def _send_worker(self):
        """Worker thread to send queued messages."""
        while self._running and self._connected:
            try:
                try:
                    message = self._send_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Send message with retry logic
                if self._send_message_with_retry(message):
                    self.stats['messages_sent'] += 1
                else:
                    logger.error(f"Failed to send message after {self._max_retries} retries")
                    self.stats['errors'] += 1
                
                self._send_queue.task_done()
                
            except Exception as e:
                logger.error(f"Send worker error: {e}")
                self.stats['errors'] += 1
                time.sleep(0.1)
    
    def _send_message_with_retry(self, message: Dict) -> bool:
        """Send message with retry logic."""
        for attempt in range(self._max_retries):
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
                        
                        # Wait for ACK if not a heartbeat
                        if message['type'] != self.MSG_HEARTBEAT:
                            self._pending_acks[message['id']] = time.time()
                            
                            # Wait for ACK
                            start_time = time.time()
                            while (message['id'] in self._pending_acks and 
                                   time.time() - start_time < self._ack_timeout):
                                time.sleep(0.01)
                            
                            # Check if ACK received
                            if message['id'] not in self._pending_acks:
                                return True
                            else:
                                # Remove from pending and retry
                                self._pending_acks.pop(message['id'], None)
                                raise Exception("ACK timeout")
                        else:
                            return True
                
            except Exception as e:
                logger.warning(f"Send attempt {attempt + 1} failed: {e}")
                self.stats['retries'] += 1
                if attempt < self._max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
        
        return False
    
    def _receive_worker(self):
        """Worker thread to receive messages from peer."""
        buffer = b''
        
        while self._running and self._connected:
            try:
                if not self._peer_socket:
                    break
                
                # Receive data
                data = self._peer_socket.recv(4096)
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
                    
                    # Process message
                    self._process_received_message(msg_data)
                
            except Exception as e:
                if self._running and self._connected:
                    logger.error(f"Receive error: {e}")
                    self.stats['errors'] += 1
                break
        
        # Connection lost
        self._handle_disconnection()
    
    def _process_received_message(self, msg_data: bytes):
        """Process a received message."""
        try:
            message = json.loads(msg_data.decode('utf-8'))
            msg_id = message.get('id')
            msg_type = message.get('type')
            payload = message.get('payload')
            
            # Send ACK for non-heartbeat messages
            if msg_type != self.MSG_HEARTBEAT and msg_type != self.MSG_ACK:
                self._send_ack(msg_id)
            
            # Handle different message types
            if msg_type == self.MSG_CHAT:
                logger.info(f"Received chat: '{payload}'")
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
                    logger.info(f"Received game data: {game_data}")
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
                ack_id = int(payload)
                self._pending_acks.pop(ack_id, None)
                
            elif msg_type == self.MSG_HEARTBEAT:
                logger.debug("Received heartbeat")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.stats['errors'] += 1
    
    def _send_ack(self, msg_id: int):
        """Send acknowledgment for received message."""
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
            logger.error(f"Failed to send ACK: {e}")
            self.stats['errors'] += 1
    
    def _heartbeat_worker(self):
        """Send periodic heartbeat messages."""
        while self._running:
            time.sleep(10)  # Send heartbeat every 10 seconds
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
    print("P2P Network Class for Pygame - Example Usage")
    print("=" * 50)
    
    # Create P2P instance
    p2p = P2PNetworkPygame("127.0.0.1", 8001, "127.0.0.1", 8002)
    
    # Start connection
    p2p.start_connection()
    
    # Example of sending messages (would be called from your pygame loop)
    time.sleep(2)  # Wait for connection
    
    if p2p.is_connected():
        # Send chat message
        p2p.send_chat("Hello from pygame!")
        
        # Send game data
        game_data = {
            "action": "move",
            "player_id": 1,
            "x": 100,
            "y": 200,
            "timestamp": time.time()
        }
        p2p.send_game(game_data)
        
        # Check for received messages
        time.sleep(1)
        messages = p2p.get_received_messages()
        for msg in messages:
            print(f"Received {msg['type']}: {msg['content']}")
    
    # Stop connection
    time.sleep(5)
    p2p.stop_connection()
    print("Example completed.")