from dqn import DQNAgent
import torch
import numpy as np
from logger import logger
from command import Command
from buttons import Buttons

class Bot:
    def __init__(self, player_number=1):
        # Set player number
        self.player_number = player_number
        
        # Define action space (12 possible button combinations)
        self.action_size = 12
        # Define state size (17 features: player x, y, health, jumping, crouching, in_move, move_id,
        # opponent x, y, health, jumping, crouching, in_move, move_id, timer, round_started, round_over)
        self.state_size = 17
        
        # Initialize DQN agent
        self.agent = DQNAgent(self.state_size, self.action_size, self.player_number)
        
        # Load model if it exists
        model_path = f'models/dqn_model_p{self.player_number}.pth'
        try:
            self.agent.load_model(model_path)
            logger.info(f"Loaded existing DQN model for player {self.player_number}")
        except:
            # Try loading the default model if player-specific model doesn't exist
            try:
                self.agent.load_model('models/dqn_model.pth')
                logger.info(f"Loaded default DQN model for player {self.player_number}")
            except:
                logger.info(f"No existing model found for player {self.player_number}, starting fresh")
            
        self.last_state = None
        self.last_game_state = None
        self.last_action = None
        
        self.fire_code = ["<", "!<", "v+<", "!v+!<", "v", "!v", "v+>", "!v+!>", ">+Y", "!>+!Y"]
        self.exe_code = 0
        self.start_fire = True
        self.remaining_code = []
        self.my_command = Command()
        self.buttn = Buttons()
        self.action_history = []
        self.combo_counter = 0
        self.defensive_mode = False
        self.aggressive_mode = False
        self.special_move_cooldown = 0
        
    def action_to_buttons(self, action):
        """Convert action index to button combination"""
        # Define button combinations
        button_combinations = [
            {'up': True},  # Jump
            {'down': True},  # Crouch
            {'left': True},  # Move left
            {'right': True},  # Move right
            {'Y': True},  # Heavy punch
            {'B': True},  # Medium punch
            {'A': True},  # Light punch
            {'X': True},  # Heavy kick
            {'L': True},  # Medium kick
            {'R': True},  # Light kick
            {'up': True, 'Y': True},  # Jump heavy punch
            {'down': True, 'B': True}  # Crouch medium punch
        ]
        
        return button_combinations[action]
        
    def update_state(self, current_game_state, player):
        """Update internal state based on game state"""
        if player == "1":
            self_player = current_game_state.player1
            opponent = current_game_state.player2
        else:
            self_player = current_game_state.player2
            opponent = current_game_state.player1
            
        # Update defensive/aggressive modes based on health
        health_ratio = self_player.health / opponent.health
        if health_ratio < 0.5:
            self.defensive_mode = True
            self.aggressive_mode = False
        elif health_ratio > 1.5:
            self.defensive_mode = False
            self.aggressive_mode = True
        else:
            self.defensive_mode = False
            self.aggressive_mode = False
            
        # Update special move cooldown
        if self.special_move_cooldown > 0:
            self.special_move_cooldown -= 1
            
        return self_player, opponent

    def execute_special_move(self, player, move_type="fireball"):
        """Execute special moves based on type"""
        if self.special_move_cooldown > 0:
            return False
            
        if move_type == "fireball":
            self.run_command(["<", "!<", "v+<", "!v+!<", "v", "!v", "v+>", "!v+!>", ">+Y", "!>+!Y"], player)
        elif move_type == "dragon_punch":
            self.run_command([">", "!>", "v+>", "!v+!>", "^+Y", "!^+!Y"], player)
        elif move_type == "spinning_kick":
            self.run_command(["v", "!v", "^+B", "!^+!B"], player)
            
        self.special_move_cooldown = 30
        return True

    def choose_action(self, self_player, opponent):
        """Choose the best action based on current state"""
        distance = abs(opponent.x_coord - self_player.x_coord)
        
        # Defensive actions
        if self.defensive_mode:
            if distance < 50:
                return "block"
            elif distance < 100:
                return "move_away"
            else:
                return "fireball"
                
        # Aggressive actions
        if self.aggressive_mode:
            if distance > 100:
                return "move_close"
            elif distance > 50:
                return "dragon_punch"
            else:
                return "combo"
                
        # Neutral actions
        if distance > 100:
            return "fireball"
        elif distance > 50:
            return "move_close"
        else:
            return "combo"

    def fight(self, game_state, player_number):
        """Main fighting logic using DQN"""
        # Update player number if needed
        self.player_number = int(player_number)
        
        # Get current state
        current_state = self.agent.get_state(game_state)
        
        # Select action
        action = self.agent.select_action(current_state)
        
        # Convert action to button combination
        button_dict = self.action_to_buttons(action)
        
        # Create Buttons object
        buttons = Buttons()
        for button, value in button_dict.items():
            # IMPORTANT: Preserve case for Y, B, A, X, L, R buttons
            if button in ['Y', 'B', 'A', 'X', 'L', 'R']:
                setattr(buttons, button, value)
            else:
                setattr(buttons, button.lower(), value)
                
        # Debug: Print button states
        pressed_buttons = []
        for btn in ['up', 'down', 'left', 'right', 'Y', 'B', 'A', 'X', 'L', 'R']:
            if getattr(buttons, btn, False):
                pressed_buttons.append(btn)
        logger.info(f"Player {self.player_number} action {action}: {pressed_buttons}")
        
        # If we have a previous state and action, store the experience
        if self.last_state is not None and self.last_action is not None:
            # Calculate reward using the game state objects
            reward = self.agent.get_reward(self.last_game_state, game_state)
            
            # Store experience in replay buffer
            self.agent.memory.push(
                self.last_state,
                self.last_action,
                reward,
                current_state,
                game_state.is_round_over
            )
            
            # Train the network
            loss = self.agent.train()
            if loss is not None:
                logger.info(f"Training loss for player {self.player_number}: {loss:.4f}")
                
            # Update target network every 1000 steps
            if len(self.agent.memory) % 1000 == 0:
                self.agent.update_target_network()
                logger.info(f"Updated target network for player {self.player_number}")
                
        # Save current state and action for next step
        self.last_state = current_state  # Store the tensor state
        self.last_game_state = game_state  # Store the game state object
        self.last_action = action
        
        # Save model periodically
        if len(self.agent.memory) % 10000 == 0:
            model_path = f'models/dqn_model_p{self.player_number}.pth'
            self.agent.save_model(model_path)
            logger.info(f"Saved DQN model for player {self.player_number}")
            
        return buttons

    def run_command(self, com, player):
        if not com:
            return
            
        if self.exe_code >= len(com):
            self.exe_code = 0
            return
            
        current_command = com[self.exe_code]
        self.buttn.init_buttons()
        
        # Parse the command string
        if "+" in current_command:
            buttons = current_command.split("+")
            for button in buttons:
                if button.startswith("!"):
                    setattr(self.buttn, button[1:].lower(), False)
                else:
                    setattr(self.buttn, button.lower(), True)
        else:
            if current_command.startswith("!"):
                setattr(self.buttn, current_command[1:].lower(), False)
            else:
                setattr(self.buttn, current_command.lower(), True)
                
        self.exe_code += 1
