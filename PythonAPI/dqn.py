import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
from logger import logger

class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, output_size)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
        
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)
        
    def __len__(self):
        return len(self.buffer)

class DQNAgent:
    def __init__(self, state_size, action_size, player_number):
        self.state_size = state_size
        self.action_size = action_size
        self.player_number = player_number
        
        # Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 64
        self.memory = ReplayBuffer(10000)
        
        # Initialize networks
        self.policy_net = DQN(state_size, action_size)
        self.target_net = DQN(state_size, action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        
    def get_state(self, game_state):
        """Convert game state to tensor"""
        # Extract relevant features from game state
        if self.player_number == 1:
            player = game_state.player1
            opponent = game_state.player2
        else:
            player = game_state.player2
            opponent = game_state.player1
            
        # Create state array with all relevant features
        state = np.array([
            player.x_coord,
            player.y_coord,
            player.health,
            player.is_jumping,
            player.is_crouching,
            player.is_player_in_move,
            player.move_id,
            opponent.x_coord,
            opponent.y_coord,
            opponent.health,
            opponent.is_jumping,
            opponent.is_crouching,
            opponent.is_player_in_move,
            opponent.move_id,
            game_state.timer,
            game_state.has_round_started,
            game_state.is_round_over
        ], dtype=np.float32)
        
        # Convert to tensor and add batch dimension
        return torch.FloatTensor(state).unsqueeze(0)
        
    def get_reward(self, game_state, next_game_state):
        """Calculate reward based on game state changes"""
        if self.player_number == 1:
            player = game_state.player1
            opponent = game_state.player2
            next_player = next_game_state.player1
            next_opponent = next_game_state.player2
        else:
            player = game_state.player2
            opponent = game_state.player1
            next_player = next_game_state.player2
            next_opponent = next_game_state.player1
            
        # Calculate health difference
        health_diff = (next_opponent.health - opponent.health) - (next_player.health - player.health)
        
        # Calculate distance to opponent
        current_dist = abs(player.x_coord - opponent.x_coord)
        next_dist = abs(next_player.x_coord - next_opponent.x_coord)
        dist_diff = current_dist - next_dist
        
        # Combine rewards
        reward = health_diff * 10 + dist_diff * 0.1
        
        return reward
        
    def select_action(self, state):
        """Select action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
            
        with torch.no_grad():
            return self.policy_net(state).argmax().item()
            
    def train(self):
        """Train the network on a batch of experiences"""
        if len(self.memory) < self.batch_size:
            return
            
        batch = self.memory.sample(self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Stack states and next_states properly
        states = torch.cat(states)  # Shape: [batch_size, state_size]
        next_states = torch.cat(next_states)  # Shape: [batch_size, state_size]
        
        # Convert other tensors
        actions = torch.tensor(actions, dtype=torch.long)  # Shape: [batch_size]
        rewards = torch.tensor(rewards, dtype=torch.float32)  # Shape: [batch_size]
        dones = torch.tensor(dones, dtype=torch.float32)  # Shape: [batch_size]
        
        # Compute Q(s_t, a)
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))  # Shape: [batch_size, 1]
        
        # Compute V(s_{t+1})
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0]  # Shape: [batch_size]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values  # Shape: [batch_size]
            
        # Compute loss and update
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()
        
    def update_target_network(self):
        """Update target network with policy network weights"""
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
    def save_model(self, path):
        """Save the model to a file"""
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, path)
        logger.info(f"Saved DQN model to {path}")
        
    def load_model(self, path):
        """Load the model from a file"""
        checkpoint = torch.load(path)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        logger.info(f"Loaded DQN model from {path}") 