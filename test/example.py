import pygame
import time
import json
from network import P2PNetworkPygame

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

class OptimizedP2PGameExample:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Optimized P2P Network Pygame Example")
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # P2P Network - high-performance version
        self.p2p = P2PNetworkPygame("127.0.0.1", 8002, "127.0.0.1", 8001)
        self.automate = False  # Set this to True for rapid automated messaging
        
        # Game state
        self.player_pos = [100, 100]
        self.peer_pos = [200, 200]
        self.messages = []
        self.input_text = ""
        self.connection_started = False
        
        # Performance tracking
        self.last_message_time = time.time()
        self.message_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # UI state
        self.typing = False
        
        # Animation for automated movement
        self.auto_direction = 1
        self.auto_frame = 0
        
    def start_connection(self):
        """Start P2P connection"""
        if not self.connection_started:
            success = self.p2p.start_connection()
            if success:
                self.connection_started = True
                self.add_message("System: P2P connection started...", GREEN)
            else:
                self.add_message("System: Failed to start connection", RED)
    
    def stop_connection(self):
        """Stop P2P connection"""
        if self.connection_started:
            self.p2p.stop_connection()
            self.connection_started = False
            self.add_message("System: P2P connection stopped", RED)
    
    def add_message(self, message, color=BLACK):
        """Add message to the display"""
        self.messages.append({"text": message, "color": color, "time": time.time()})
        # Keep only last 15 messages for better display
        if len(self.messages) > 15:
            self.messages.pop(0)
    
    def send_chat_message(self, message):
        """Send chat message to peer"""
        if self.p2p.is_connected():
            success = self.p2p.send_chat(message)
            if success:
                self.add_message(f"You (Chat): {message}", BLUE)
                self.message_count += 1
            else:
                self.add_message("Failed to send chat message", RED)
        else:
            self.add_message("Not connected to peer", RED)
    
    def send_game_data(self, data):
        """Send game data to peer"""
        if self.p2p.is_connected():
            success = self.p2p.send_game(data)
            if success:
                self.add_message(f"You (Game): {data}", GREEN)
                self.message_count += 1
            else:
                self.add_message("Failed to send game data", RED)
        else:
            self.add_message("Not connected to peer", RED)
    
    def handle_automation(self):
        """Handle automated rapid messaging"""
        if self.automate and self.p2p.is_connected():
            # Send rapid game updates (simulating high-frequency game state)
            self.auto_frame += 1
            
            # Calculate smooth movement
            x_offset = int(50 * pygame.math.Vector2(1, 0).rotate(self.auto_frame * 2).x)
            y_offset = int(30 * pygame.math.Vector2(1, 0).rotate(self.auto_frame * 3).y)
            
            new_x = 400 + x_offset
            new_y = 300 + y_offset
            
            # Update player position smoothly
            self.player_pos[0] = new_x
            self.player_pos[1] = new_y
            
            # Send high-frequency game data
            game_data = {
                "action": "move",
                "player_id": 1,
                "x": self.player_pos[0],
                "y": self.player_pos[1],
                "frame": self.auto_frame,
                "velocity_x": x_offset,
                "velocity_y": y_offset,
                "timestamp": time.time()
            }
            
            self.p2p.send_game(game_data)
            
            # Occasionally send chat messages during automation
            if self.auto_frame % 60 == 0:  # Every ~1 second at 60 FPS
                self.p2p.send_chat(f"Auto message {self.auto_frame // 60}")
    
    def handle_events(self):
        """Handle pygame events"""
        if not self.automate:
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_UP]:
                self.player_pos[1] -= 20
                self.send_game_data({
                    "action": "move",
                    "player_id": 1,
                    "x": self.player_pos[0],
                    "y": self.player_pos[1],
                    "direction": "up"
                })
            
            elif keys[pygame.K_DOWN]:
                self.player_pos[1] += 20
                self.send_game_data({
                    "action": "move",
                    "player_id": 1,
                    "x": self.player_pos[0],
                    "y": self.player_pos[1],
                    "direction": "down"
                })
            
            elif keys[pygame.K_LEFT]:
                self.player_pos[0] -= 20
                self.send_game_data({
                    "action": "move",
                    "player_id": 1,
                    "x": self.player_pos[0],
                    "y": self.player_pos[1],
                    "direction": "left"
                })
            
            elif keys[pygame.K_RIGHT]:
                self.player_pos[0] += 20
                self.send_game_data({
                    "action": "move",
                    "player_id": 1,
                    "x": self.player_pos[0],
                    "y": self.player_pos[1],
                    "direction": "right"
                        })
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_F1:
                    self.start_connection()
                
                elif event.key == pygame.K_F2:
                    self.stop_connection()
                
                elif event.key == pygame.K_F3:
                    # Toggle automation (your test case)
                    self.automate = not self.automate
                    status = "ON" if self.automate else "OFF"
                    self.add_message(f"System: Automation {status}", YELLOW)
                    if self.automate:
                        self.auto_frame = 0  # Reset animation
                
                elif event.key == pygame.K_RETURN:
                    if self.typing and self.input_text.strip():
                        self.send_chat_message(self.input_text.strip())
                        self.input_text = ""
                    self.typing = not self.typing
                
                elif event.key == pygame.K_BACKSPACE:
                    if self.typing:
                        self.input_text = self.input_text[:-1]
                
                elif self.typing:
                    self.input_text += event.unicode
                
                # Manual movement keys (only when not automating)
                
                    
                    # elif event.key == pygame.K_SPACE:
                    #     # Send attack game data
                    #     self.send_game_data({
                    #         "action": "attack",
                    #         "player_id": 1,
                    #         "x": self.player_pos[0],
                    #         "y": self.player_pos[1],
                    #         "damage": 25
                    #     })
    
    def process_received_messages(self):
        """Process messages received from peer"""
        messages = self.p2p.get_received_messages()
        
        for msg in messages:
            if msg['type'] == 'chat':
                self.add_message(f"Peer (Chat): {msg['content']}", BLUE)
            
            elif msg['type'] == 'game':
                game_data = msg['content']
                
                # Handle different game actions
                if game_data.get('action') == 'move':
                    # Update peer position smoothly
                    self.peer_pos[0] = game_data.get('x', self.peer_pos[0])
                    self.peer_pos[1] = game_data.get('y', self.peer_pos[1])
                    
                    # Only show movement messages occasionally to avoid spam
                    frame = game_data.get('frame', 0)
                    if frame % 120 == 0:  # Every 2 seconds
                        self.add_message(f"Peer moved to ({self.peer_pos[0]}, {self.peer_pos[1]})", GREEN)
                
                elif game_data.get('action') == 'attack':
                    damage = game_data.get('damage', 0)
                    self.add_message(f"Peer attacked! Damage: {damage}", RED)
                
                else:
                    self.add_message(f"Peer (Game): {game_data}", GREEN)
    
    def draw(self):
        """Draw everything on screen"""
        self.screen.fill(WHITE)
        
        # Draw connection status
        if self.p2p.is_connected():
            status_text = self.font.render("Status: CONNECTED", True, GREEN)
        elif self.connection_started:
            status_text = self.font.render("Status: CONNECTING...", True, GRAY)
        else:
            status_text = self.font.render("Status: DISCONNECTED", True, RED)
        
        self.screen.blit(status_text, (10, 10))
        
        # Draw automation status
        auto_status = "ON" if self.automate else "OFF"
        auto_color = YELLOW if self.automate else GRAY
        auto_text = self.font.render(f"Automation: {auto_status}", True, auto_color)
        self.screen.blit(auto_text, (250, 10))
        
        # Draw high-performance statistics
        stats = self.p2p.get_stats()
        stats_text = self.small_font.render(
            f"Sent: {stats['messages_sent']} | Received: {stats['messages_received']} | Errors: {stats['errors']} | Retries: {stats['retries']}", 
            True, BLACK
        )
        self.screen.blit(stats_text, (10, 40))
        
        # Draw performance metrics
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.last_fps_time = current_time
            self.fps_counter = self.clock.get_fps()
        
        perf_text = self.small_font.render(
            f"FPS: {self.fps_counter:.1f} | Chat: {stats['chat_sent']}/{stats['chat_received']} | Game: {stats['game_sent']}/{stats['game_received']}", 
            True, BLACK
        )
        self.screen.blit(perf_text, (10, 60))
        
        # Draw instructions
        instructions = [
            "F1: Start Connection | F2: Stop | F3: Toggle Automation | ESC: Quit",
            "Arrow Keys: Move (manual) | Space: Attack | Enter: Chat",
            "Automation sends rapid messages (~60/sec) to test concurrency"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (10, 90 + i * 20))
        
        # Draw players
        # Your player (blue square, yellow border if automating)
        player_color = BLUE
        if self.automate:
            pygame.draw.rect(self.screen, YELLOW, (self.player_pos[0] - 2, self.player_pos[1] - 2, 34, 34))
        
        pygame.draw.rect(self.screen, player_color, (self.player_pos[0], self.player_pos[1], 30, 30))
        player_label = self.small_font.render("You", True, BLACK)
        self.screen.blit(player_label, (self.player_pos[0], self.player_pos[1] - 20))
        
        # Peer player (red square)
        pygame.draw.rect(self.screen, RED, (self.peer_pos[0], self.peer_pos[1], 30, 30))
        peer_label = self.small_font.render("Peer", True, BLACK)
        self.screen.blit(peer_label, (self.peer_pos[0], self.peer_pos[1] - 20))
        
        # Draw messages (showing more with smaller font)
        y_offset = SCREEN_HEIGHT - 300
        for i, msg in enumerate(self.messages):
            if i < 12:  # Show more messages
                text = self.small_font.render(msg["text"][:70] + "..." if len(msg["text"]) > 70 else msg["text"], True, msg["color"])
                self.screen.blit(text, (10, y_offset + i * 18))
        
        # Draw input box
        if self.typing:
            input_box = pygame.Rect(10, SCREEN_HEIGHT - 40, SCREEN_WIDTH - 20, 30)
            pygame.draw.rect(self.screen, WHITE, input_box)
            pygame.draw.rect(self.screen, BLACK, input_box, 2)
            
            input_surface = self.font.render(f"Chat: {self.input_text}|", True, BLACK)
            self.screen.blit(input_surface, (15, SCREEN_HEIGHT - 35))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("Optimized P2P Pygame Example Started!")
        print("=" * 50)
        print("Instructions:")
        print("- Press F1 to start P2P connection")
        print("- Press F2 to stop P2P connection") 
        print("- Press F3 to toggle automation (your test case!)")
        print("- Use arrow keys to move manually")
        print("- Press Space to attack")
        print("- Press Enter to type chat messages")
        print("- Open another instance to test concurrent messaging!")
        print("=" * 50)
        print("\nWhen automation is ON:")
        print("- Sends ~60 game updates per second")
        print("- Sends chat messages every second")
        print("- Tests your exact scenario: rapid automated messages")
        print("- Other peer can still send/receive normally")
        print("=" * 50)
        
        while self.running:
            # Handle automation (your test scenario)
            self.handle_automation()
            
            # Handle user input
            self.handle_events()
            
            # Process received messages
            self.process_received_messages()
            
            # Draw everything
            self.draw()
            
            # Maintain 60 FPS
            self.clock.tick(60)
        
        # Cleanup
        self.stop_connection()
        pygame.quit()


def test_two_instances():
    """
    Instructions for testing the exact scenario you described:
    
    1. Run this script in two separate terminals/instances
    2. In instance 1: Press F1 to connect
    3. In instance 2: Change the ports and press F1
    4. In one instance: Press F3 to enable automation
    5. Watch messages flow smoothly in both directions!
    """
    print("\nTo test your automation scenario:")
    print("1. Run two instances of this script")
    print("2. Connect both (F1)")
    print("3. Enable automation in one (F3)")
    print("4. Send manual messages in the other")
    print("5. Watch smooth concurrent messaging!")

if __name__ == "__main__":
    # Show testing instructions
    test_two_instances()
    
    # Run the optimized example
    app = OptimizedP2PGameExample()
    app.run()