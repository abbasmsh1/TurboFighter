import csv
import os
from datetime import datetime
from logger import logger

class DataRecorder:
    def __init__(self):
        self.records = []
        self.start_time = datetime.now()
        self.filename = "game_data.csv"  # Use a fixed filename
        self.csv_file = None
        self.csv_writer = None
        self.frame_count = 0
        self.current_round = 1
        
        # Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # Initialize CSV file
        self.initialize_csv()
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Data Recorder initialized")
        
    def initialize_csv(self):
        """Initialize CSV file with headers"""
        filepath = os.path.join('data', self.filename)
        
        # Check if file exists
        file_exists = os.path.isfile(filepath)
        
        # Open file in append mode
        self.csv_file = open(filepath, 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Write headers only if file is new
        if not file_exists:
            headers = [
                'timestamp', 'round', 'frame',
                # Player 1 state
                'p1_character', 'p1_health', 'p1_x', 'p1_y', 
                'p1_jumping', 'p1_crouching', 'p1_in_move', 'p1_move_id',
                # Player 2 state
                'p2_character', 'p2_health', 'p2_x', 'p2_y',
                'p2_jumping', 'p2_crouching', 'p2_in_move', 'p2_move_id',
                # Game state
                'timer', 'has_round_started', 'is_round_over', 'fight_result',
                # Player 1 buttons
                'p1_up', 'p1_down', 'p1_left', 'p1_right',
                'p1_Y', 'p1_B', 'p1_A', 'p1_X', 'p1_L', 'p1_R',
                # Player 2 buttons
                'p2_up', 'p2_down', 'p2_left', 'p2_right',
                'p2_Y', 'p2_B', 'p2_A', 'p2_X', 'p2_L', 'p2_R'
            ]
            self.csv_writer.writerow(headers)
            logger.info(f"Created new CSV file: {filepath}")
        else:
            logger.info(f"Appending to existing CSV file: {filepath}")
        
    def get_button_name(self, button_value):
        """Convert button value to readable name"""
        return "Pressed" if button_value else "Released"
        
    def print_button_state(self, player_num, button_name, state):
        """Print button state in a readable format"""
        if state:  # Only print when button is pressed
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Player {player_num} {button_name}: {self.get_button_name(state)}")
        
    def print_game_state(self, game_state):
        """Print current game state"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S.%f')}] Game State Update:")
        print(f"Round: {self.current_round}, Timer: {game_state.timer}")
        print(f"Round Started: {game_state.has_round_started}, Round Over: {game_state.is_round_over}")
        
        # Player 1 info
        print(f"Player 1 - Character: {game_state.player1.player_id}, Health: {game_state.player1.health}")
        print(f"Position: ({game_state.player1.x_coord}, {game_state.player1.y_coord})")
        print(f"Jumping: {game_state.player1.is_jumping}, Crouching: {game_state.player1.is_crouching}")
        print(f"In Move: {game_state.player1.is_player_in_move}, Move ID: {game_state.player1.move_id}")
        
        # Player 2 info
        print(f"Player 2 - Character: {game_state.player2.player_id}, Health: {game_state.player2.health}")
        print(f"Position: ({game_state.player2.x_coord}, {game_state.player2.y_coord})")
        print(f"Jumping: {game_state.player2.is_jumping}, Crouching: {game_state.player2.is_crouching}")
        print(f"In Move: {game_state.player2.is_player_in_move}, Move ID: {game_state.player2.move_id}")
        
    def record_frame(self, game_state, player1_buttons, player2_buttons):
        """Record a frame of game data and save to CSV"""
        self.frame_count += 1
        current_time = (datetime.now() - self.start_time).total_seconds()
        
        # Update round number when round is over
        if game_state.is_round_over:
            self.current_round += 1
        
        # Print frame count every 60 frames (approximately 1 second)
        if self.frame_count % 60 == 0:
            print(f"\n[{datetime.now().strftime('%H:%M:%S.%f')}] Frame {self.frame_count} - Data still being received")
        
        # Print game state every 180 frames (approximately 3 seconds)
        if self.frame_count % 180 == 0:
            self.print_game_state(game_state)
        
        # Print button states for player 1
        self.print_button_state(1, "Up", player1_buttons.up)
        self.print_button_state(1, "Down", player1_buttons.down)
        self.print_button_state(1, "Left", player1_buttons.left)
        self.print_button_state(1, "Right", player1_buttons.right)
        self.print_button_state(1, "Y (Heavy Punch)", player1_buttons.Y)
        self.print_button_state(1, "B (Medium Punch)", player1_buttons.B)
        self.print_button_state(1, "A (Light Punch)", player1_buttons.A)
        self.print_button_state(1, "X (Heavy Kick)", player1_buttons.X)
        self.print_button_state(1, "L (Medium Kick)", player1_buttons.L)
        self.print_button_state(1, "R (Light Kick)", player1_buttons.R)
        
        # Print button states for player 2
        self.print_button_state(2, "Up", player2_buttons.up)
        self.print_button_state(2, "Down", player2_buttons.down)
        self.print_button_state(2, "Left", player2_buttons.left)
        self.print_button_state(2, "Right", player2_buttons.right)
        self.print_button_state(2, "Y (Heavy Punch)", player2_buttons.Y)
        self.print_button_state(2, "B (Medium Punch)", player2_buttons.B)
        self.print_button_state(2, "A (Light Punch)", player2_buttons.A)
        self.print_button_state(2, "X (Heavy Kick)", player2_buttons.X)
        self.print_button_state(2, "L (Medium Kick)", player2_buttons.L)
        self.print_button_state(2, "R (Light Kick)", player2_buttons.R)
        
        # Get fight result (if available)
        fight_result = getattr(game_state, 'fight_result', 'None')
        
        # Prepare row data with all important information
        row = [
            current_time,
            self.current_round,
            self.frame_count,
            # Player 1 state
            game_state.player1.player_id,
            game_state.player1.health,
            game_state.player1.x_coord,
            game_state.player1.y_coord,
            game_state.player1.is_jumping,
            game_state.player1.is_crouching,
            game_state.player1.is_player_in_move,
            game_state.player1.move_id,
            # Player 2 state
            game_state.player2.player_id,
            game_state.player2.health,
            game_state.player2.x_coord,
            game_state.player2.y_coord,
            game_state.player2.is_jumping,
            game_state.player2.is_crouching,
            game_state.player2.is_player_in_move,
            game_state.player2.move_id,
            # Game state
            game_state.timer,
            game_state.has_round_started,
            game_state.is_round_over,
            fight_result,
            # Player 1 buttons
            player1_buttons.up,
            player1_buttons.down,
            player1_buttons.left,
            player1_buttons.right,
            player1_buttons.Y,
            player1_buttons.B,
            player1_buttons.A,
            player1_buttons.X,
            player1_buttons.L,
            player1_buttons.R,
            # Player 2 buttons
            player2_buttons.up,
            player2_buttons.down,
            player2_buttons.left,
            player2_buttons.right,
            player2_buttons.Y,
            player2_buttons.B,
            player2_buttons.A,
            player2_buttons.X,
            player2_buttons.L,
            player2_buttons.R
        ]
        
        # Write to CSV
        self.csv_writer.writerow(row)
        self.csv_file.flush()  # Ensure data is written to disk
        
        # Also store in memory for potential analysis
        self.records.append(row)
        
    def close(self):
        """Close the CSV file"""
        if self.csv_file:
            self.csv_file.close()
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Data Recorder closed. Total frames recorded: {self.frame_count}")
            logger.info(f"Closed CSV file: {self.filename}")
            
    def __del__(self):
        """Ensure file is closed when object is destroyed"""
        self.close() 