# Memory addresses for Street Fighter II Turbo (U) [smc]
MEMORY_ADDRESSES = {
    'PLAYER1': {
        'X_POS': 0x7E0F80,  # Player 1 X coordinate
        'Y_POS': 0x7E0F82,  # Player 1 Y coordinate
        'HEALTH': 0x7E0F84,  # Player 1 health
        'STATE': 0x7E0F86,   # Player 1 state (standing, jumping, etc.)
    },
    'PLAYER2': {
        'X_POS': 0x7E0F88,  # Player 2 X coordinate
        'Y_POS': 0x7E0F8A,  # Player 2 Y coordinate
        'HEALTH': 0x7E0F8C,  # Player 2 health
        'STATE': 0x7E0F8E,   # Player 2 state
    },
    'GAME': {
        'TIMER': 0x7E0F90,    # Round timer
        'ROUND': 0x7E0F92,    # Current round
        'ROUND_STATE': 0x7E0F94,  # Round state (0=not started, 1=in progress, 2=over)
    }
}

# Network configuration
NETWORK_CONFIG = {
    'HOST': '127.0.0.1',
    'PORT_P1': 9998,
    'PORT_P2': 10001,
    'BUFFER_SIZE': 4096
}

# Button mappings
BUTTON_MAPPINGS = {
    'UP': '^',
    'DOWN': 'v',
    'LEFT': '<',
    'RIGHT': '>',
    'Y': 'Y',
    'B': 'B',
    'A': 'A',
    'X': 'X',
    'L': 'L',
    'R': 'R',
    'SELECT': 'select',
    'START': 'start'
}

# Special move inputs
SPECIAL_MOVES = {
    'FIREBALL': ['<', '!<', 'v+<', '!v+!<', 'v', '!v', 'v+>', '!v+!>', '>+Y', '!>+!Y'],
    'DRAGON_PUNCH': ['>', '!>', 'v+>', '!v+!>', '^+Y', '!^+!Y'],
    'SPINNING_KICK': ['v', '!v', '^+B', '!^+!B']
}

# Bot configuration
BOT_CONFIG = {
    'DEFENSIVE_HEALTH_RATIO': 0.5,
    'AGGRESSIVE_HEALTH_RATIO': 1.5,
    'SPECIAL_MOVE_COOLDOWN': 30,
    'COMBO_LENGTH': 3,
    'REACTION_TIME': 0.1  # seconds
}

# Logging configuration
LOGGING_CONFIG = {
    'LOG_FILE': 'bot.log',
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(levelname)s - %(message)s'
} 