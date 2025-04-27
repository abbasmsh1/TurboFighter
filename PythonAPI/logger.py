import logging
import os
from config import LOGGING_CONFIG

def setup_logger():
    """Setup and configure the logger"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Configure logging
    logging.basicConfig(
        filename=os.path.join('logs', LOGGING_CONFIG['LOG_FILE']),
        level=getattr(logging, LOGGING_CONFIG['LOG_LEVEL']),
        format=LOGGING_CONFIG['LOG_FORMAT']
    )
    
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(LOGGING_CONFIG['LOG_FORMAT'])
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    return logging.getLogger(__name__)

# Create logger instance
logger = setup_logger()

def log_game_state(game_state):
    """Log the current game state"""
    logger.info(f"Game State - Round: {game_state.round}, Timer: {game_state.timer}")
    logger.info(f"Player 1 - Health: {game_state.player1.health}, Position: ({game_state.player1.x_coord}, {game_state.player1.y_coord})")
    logger.info(f"Player 2 - Health: {game_state.player2.health}, Position: ({game_state.player2.x_coord}, {game_state.player2.y_coord})")

def log_bot_action(action, player):
    """Log bot actions"""
    logger.info(f"Bot Action - Player {player}: {action}")

def log_error(error_msg, exc_info=None):
    """Log errors"""
    logger.error(error_msg, exc_info=exc_info)

def log_warning(warning_msg):
    """Log warnings"""
    logger.warning(warning_msg)

def log_debug(debug_msg):
    """Log debug messages"""
    logger.debug(debug_msg) 