import socket
import json
from game_state import GameState
from bot import Bot
from data_recorder import DataRecorder
from logger import logger
from command import Command
from buttons import Buttons
import sys
import os
import threading
import time
from datetime import datetime

def log_action_buttons(player_num, buttons):
    """Log detailed information about action button presses"""
    action_buttons_pressed = []
    
    # Check individual button states
    logging_dict = {
        'Y': getattr(buttons, 'Y', False),
        'B': getattr(buttons, 'B', False),
        'A': getattr(buttons, 'A', False),
        'X': getattr(buttons, 'X', False),
        'L': getattr(buttons, 'L', False),
        'R': getattr(buttons, 'R', False)
    }
    
    # Log all button states for debugging
    logger.info(f"P{player_num} button states: Y={logging_dict['Y']}, B={logging_dict['B']}, A={logging_dict['A']}, X={logging_dict['X']}, L={logging_dict['L']}, R={logging_dict['R']}")
    
    # Check which action buttons are pressed
    if buttons.Y: action_buttons_pressed.append("Y (Heavy Punch)")
    if buttons.B: action_buttons_pressed.append("B (Medium Punch)")
    if buttons.A: action_buttons_pressed.append("A (Light Punch)")
    if buttons.X: action_buttons_pressed.append("X (Heavy Kick)")
    if buttons.L: action_buttons_pressed.append("L (Medium Kick)")
    if buttons.R: action_buttons_pressed.append("R (Light Kick)")
    
    # If any action buttons are pressed, log them
    if action_buttons_pressed:
        player_type = "Human" if player_num == 1 else "AI"
        logger.info(f"Player {player_num} ({player_type}) ACTION buttons: {', '.join(action_buttons_pressed)}")

def button_state_to_string(buttons):
    """Convert Buttons object to readable string of pressed buttons"""
    # Debug raw button access
    y_value = getattr(buttons, 'Y', 'NotFound')
    b_value = getattr(buttons, 'B', 'NotFound')
    a_value = getattr(buttons, 'A', 'NotFound')
    x_value = getattr(buttons, 'X', 'NotFound')
    logger.debug(f"Raw button values - Y:{y_value}, B:{b_value}, A:{a_value}, X:{x_value}")
    
    pressed = []
    direction_buttons = []
    action_buttons = []
    
    # Direction buttons
    if buttons.up: direction_buttons.append("Up")
    if buttons.down: direction_buttons.append("Down")
    if buttons.left: direction_buttons.append("Left")
    if buttons.right: direction_buttons.append("Right")
    
    # Action buttons - highlight these
    if getattr(buttons, 'Y', False): action_buttons.append("Y(Heavy Punch)")
    if getattr(buttons, 'B', False): action_buttons.append("B(Medium Punch)")
    if getattr(buttons, 'A', False): action_buttons.append("A(Light Punch)")
    if getattr(buttons, 'X', False): action_buttons.append("X(Heavy Kick)")
    if getattr(buttons, 'L', False): action_buttons.append("L(Medium Kick)")
    if getattr(buttons, 'R', False): action_buttons.append("R(Light Kick)")
    
    # Combine all pressed buttons
    if direction_buttons:
        pressed.append("Direction: " + ", ".join(direction_buttons))
    if action_buttons:
        pressed.append("Action: " + ", ".join(action_buttons))
    
    if not pressed:
        return "None"
    return " | ".join(pressed)

def connect(port):
    #For making a connection with the game
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(5)
    (client_socket, _) = server_socket.accept()
    print (f"Connected to game on port {port}!")
    return client_socket

def send(client_socket, command):
    #This function will send your updated command to Bizhawk so that game reacts according to your command.
    command_dict = command.object_to_dict()
    pay_load = json.dumps(command_dict).encode()
    client_socket.sendall(pay_load)

def receive(client_socket):
    #receive the game state and return game state
    pay_load = client_socket.recv(4096)
    input_dict = json.loads(pay_load.decode())
    game_state = GameState(input_dict)
    return game_state

class Player:
    def __init__(self, player_number):
        self.player_number = player_number
        self.port = 9999 if player_number == 1 else 9999
        self.client_socket = None
        self.bot = Bot(player_number)
        self.current_game_state = None
        self.buttons = Buttons()
        self.command = Command()
        self.connected = False
        
    def connect(self):
        try:
            self.client_socket = connect(self.port)
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Player {self.player_number} connection error: {e}")
            return False
            
    def process_frame(self):
        if not self.connected:
            return None, None
            
        try:
            self.current_game_state = receive(self.client_socket)
            self.buttons = self.bot.fight(self.current_game_state, str(self.player_number))
            
            # Create command object from buttons
            self.command = Command()
            if self.player_number == 1:
                self.command.player_buttons = self.buttons
            else:
                self.command.player2_buttons = self.buttons
                
            send(self.client_socket, self.command)
            
            return self.current_game_state, self.buttons
        except Exception as e:
            logger.error(f"Player {self.player_number} frame processing error: {e}")
            self.connected = False
            return None, None
            
    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            self.connected = False

def main():
    # Check if we're running in single player or two player mode
    single_player_mode = len(sys.argv) > 1 and sys.argv[1] in ['1', '2']
    
    # Create player instances
    player1 = Player(1)
    player2 = Player(2)
    recorder = DataRecorder()
    
    # For testing: create a test buttons object with all action buttons pressed
    test_buttons = Buttons()
    test_buttons.Y = True
    test_buttons.B = True
    test_buttons.A = True
    test_buttons.X = True
    test_buttons.L = True
    test_buttons.R = True
    
    # Print a debug message with test button states
    logger.info("TEST BUTTONS - Created test buttons object with action buttons")
    log_action_buttons(999, test_buttons)  # Test player number 999
    
    # Connect players
    if single_player_mode:
        player_num = int(sys.argv[1])
        if player_num == 1:
            if not player1.connect():
                logger.error("Failed to connect player 1")
                return
                
            # Make sure player 2's bot is properly initialized as an opponent
            player2.bot = Bot(2)  # Reinitialize with player number 2
            player2.connected = False  # Not physically connected
        else:
            if not player2.connect():
                logger.error("Failed to connect player 2")
                return
                
            # Make sure player 1's bot is properly initialized as an opponent
            player1.bot = Bot(1)  # Reinitialize with player number 1
            player1.connected = False  # Not physically connected
    else:
        # Connect both players for two-player mode
        player1_connected = player1.connect()
        player2_connected = player2.connect()
        
        if not player1_connected or not player2_connected:
            logger.error("Failed to connect one or both players")
            return
    
    try:
        # Main game loop
        while True:
            # Process player 1 if connected (human player 1)
            if player1.connected:
                game_state1, p1_buttons = player1.process_frame()
                
                # If we have a valid game state, generate AI moves as player 2
                if game_state1 is not None:
                    # Generate AI moves for player 2
                    p2_buttons = player2.bot.fight(game_state1, "2")
                    logger.info(f"AI (P2) pressed: {button_state_to_string(p2_buttons)}")
                else:
                    p2_buttons = Buttons()
            # Process player 2 if connected (human player 2)
            elif player2.connected:
                game_state2, human_p2_buttons = player2.process_frame()
                
                # If we have a valid game state, generate AI moves as player 1
                # but record them as player 2 for consistency
                if game_state2 is not None:
                    # Generate AI moves (technically as player 1)
                    ai_buttons = player1.bot.fight(game_state2, "1")
                    logger.info(f"AI (recorded as P2) pressed: {button_state_to_string(ai_buttons)}")
                    
                    # Record human as player 1 and AI as player 2
                    p1_buttons = human_p2_buttons  # Human actions recorded as P1
                    p2_buttons = ai_buttons        # AI actions recorded as P2
                else:
                    p1_buttons = Buttons()
                    p2_buttons = Buttons()
            else:
                # No players connected
                game_state1 = None
                game_state2 = None
                p1_buttons = Buttons()
                p2_buttons = Buttons()
                
            # Use whichever game state is available
            game_state = game_state1 if game_state1 is not None else game_state2
                
            # Record the frame if we have a valid game state
            if game_state is not None:                
                # Record both players' actions
                recorder.record_frame(
                    game_state,
                    p1_buttons,
                    p2_buttons
                )
                
                # Debug output for both players' actions
                print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] P1 buttons: {button_state_to_string(p1_buttons)}")
                print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] P2 buttons (AI): {button_state_to_string(p2_buttons)}")
                
                # Log specific action button presses with more detail
                log_action_buttons(1, p1_buttons)
                log_action_buttons(2, p2_buttons)
            
            # Check if round is over
            if (game_state is not None and game_state.is_round_over) or \
               (not player1.connected and not player2.connected):
                break
                
            # Small delay to prevent CPU hogging
            time.sleep(0.01)
            
        logger.info("Round finished")
        
    except KeyboardInterrupt:
        logger.info("Recording interrupted by user")
    except Exception as e:
        logger.error(f"Error during recording: {str(e)}")
    finally:
        player1.disconnect()
        player2.disconnect()
        recorder.close()

if __name__ == '__main__':
   main()
