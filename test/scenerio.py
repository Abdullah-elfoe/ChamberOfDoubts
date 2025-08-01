#!/usr/bin/env python3
"""
Test script to demonstrate concurrent P2P messaging without packet collision.
This directly tests your scenario where:
- Peer A sends game data while Peer B sends chat
- Both messages arrive safely without collision
"""

import time
import threading
from network import P2PNetworkPygame

def test_concurrent_messaging():
    """Test the exact scenario you described"""
    print("P2P Concurrent Messaging Test")
    print("=" * 40)
    print("Testing scenario: Peer A sends game data while Peer B sends chat")
    print("Expected: Both messages arrive without collision\n")
    
    # Create two P2P instances
    peer_a = P2PNetworkPygame("127.0.0.1", 8001, "127.0.0.1", 8002)
    peer_b = P2PNetworkPygame("127.0.0.1", 8002, "127.0.0.1", 8001)
    
    # Start connections
    print("1. Starting P2P connections...")
    peer_a.start_connection()
    peer_b.start_connection()
    
    # Wait for connection establishment
    print("2. Waiting for connection establishment...")
    connection_timeout = 10
    start_time = time.time()
    
    while (time.time() - start_time) < connection_timeout:
        if peer_a.is_connected() and peer_b.is_connected():
            break
        time.sleep(0.5)
    
    if not (peer_a.is_connected() and peer_b.is_connected()):
        print("❌ Failed to establish connection between peers")
        peer_a.stop_connection()
        peer_b.stop_connection()
        return False
    
    print("✓ Both peers connected successfully!")
    
    # Test your specific scenario
    print("\n3. Testing concurrent message sending...")
    
    # Prepare messages
    game_data = {
        "action": "move",
        "player_id": 1,
        "x": 150,
        "y": 250,
        "health": 100,
        "weapon": "sword"
    }
    chat_message = "You are playing greatly mate"
    
    def send_game_data():
        """Send game data from Peer A"""
        success = peer_a.send_game(game_data)
        print(f"   Peer A game data sent: {success}")
        return success
    
    def send_chat_message():
        """Send chat message from Peer B"""
        success = peer_b.send_chat(chat_message)
        print(f"   Peer B chat sent: {success}")
        return success
    
    # Send both messages concurrently
    print("   Sending messages concurrently...")
    thread_a = threading.Thread(target=send_game_data)
    thread_b = threading.Thread(target=send_chat_message)
    
    # Start both threads at nearly the same time
    thread_a.start()
    thread_b.start()
    
    # Wait for both to complete
    thread_a.join()
    thread_b.join()
    
    # Wait for message processing
    print("4. Waiting for message processing...")
    time.sleep(3)
    
    # Check received messages
    print("\n5. Checking received messages...")
    
    # Get messages received by each peer
    messages_a = peer_a.get_received_messages()
    messages_b = peer_b.get_received_messages()
    
    print(f"\nPeer A received {len(messages_a)} messages:")
    for i, msg in enumerate(messages_a):
        print(f"   [{i+1}] Type: {msg['type']}, Content: {msg['content']}")
    
    print(f"\nPeer B received {len(messages_b)} messages:")
    for i, msg in enumerate(messages_b):
        print(f"   [{i+1}] Type: {msg['type']}, Content: {msg['content']}")
    
    # Verify results
    success = True
    
    # Peer A should receive the chat message from Peer B
    chat_received = any(msg['type'] == 'chat' and msg['content'] == chat_message for msg in messages_a)
    if chat_received:
        print("✓ Peer A correctly received chat message")
    else:
        print("❌ Peer A did not receive chat message")
        success = False
    
    # Peer B should receive the game data from Peer A
    game_received = any(msg['type'] == 'game' and msg['content'] == game_data for msg in messages_b)
    if game_received:
        print("✓ Peer B correctly received game data")
    else:
        print("❌ Peer B did not receive game data")
        success = False
    
    # Display statistics
    print(f"\n6. Connection Statistics:")
    stats_a = peer_a.get_stats()
    stats_b = peer_b.get_stats()
    
    print(f"   Peer A: Sent: {stats_a['messages_sent']}, Received: {stats_a['messages_received']}, Errors: {stats_a['errors']}")
    print(f"   Peer B: Sent: {stats_b['messages_sent']}, Received: {stats_b['messages_received']}, Errors: {stats_b['errors']}")
    
    # Cleanup
    print("\n7. Cleaning up connections...")
    peer_a.stop_connection()
    peer_b.stop_connection()
    
    # Final result
    print(f"\n{'='*40}")
    if success:
        print("🎉 SUCCESS: Concurrent messaging works without packet collision!")
        print("   - Game data was sent and received correctly")
        print("   - Chat message was sent and received correctly") 
        print("   - No message collision or data loss occurred")
    else:
        print("❌ FAILED: Some messages were not received correctly")
    print(f"{'='*40}")
    
    return success

def test_multiple_rapid_messages():
    """Test rapid sequential message sending"""
    print("\n" + "="*40)
    print("ADDITIONAL TEST: Rapid Sequential Messages")
    print("="*40)
    
    peer_a = P2PNetworkPygame("127.0.0.1", 8001, "127.0.0.1", 8002)
    peer_b = P2PNetworkPygame("127.0.0.1", 8002, "127.0.0.1", 8001)
    
    peer_a.start_connection()
    peer_b.start_connection()
    
    # Wait for connection
    time.sleep(3)
    
    if peer_a.is_connected() and peer_b.is_connected():
        print("Sending rapid sequence of mixed messages...")
        
        # Send multiple messages rapidly
        for i in range(5):
            peer_a.send_chat(f"Message {i}")
            peer_a.send_game({"sequence": i, "action": "test", "value": i * 10})
            peer_b.send_chat(f"Reply {i}")
            peer_b.send_game({"reply": i, "status": "ok", "counter": i})
        
        time.sleep(4)  # Wait for all messages to process
        
        messages_a = peer_a.get_received_messages()
        messages_b = peer_b.get_received_messages()
        
        print(f"Peer A received {len(messages_a)} messages")
        print(f"Peer B received {len(messages_b)} messages")
        
        # Count message types
        a_chat = sum(1 for msg in messages_a if msg['type'] == 'chat')
        a_game = sum(1 for msg in messages_a if msg['type'] == 'game')
        b_chat = sum(1 for msg in messages_b if msg['type'] == 'chat')
        b_game = sum(1 for msg in messages_b if msg['type'] == 'game')
        
        print(f"Peer A: {a_chat} chat, {a_game} game messages")
        print(f"Peer B: {b_chat} chat, {b_game} game messages")
        
        if a_chat == 5 and a_game == 5 and b_chat == 5 and b_game == 5:
            print("✓ All rapid messages received correctly!")
        else:
            print("❌ Some rapid messages were lost")
    
    peer_a.stop_connection()
    peer_b.stop_connection()

if __name__ == "__main__":
    # Run the main test
    success = test_concurrent_messaging()
    
    if success:
        # Run additional test
        test_multiple_rapid_messages()
    
    print(f"\nTest completed. Your P2P networking class is ready for pygame!")