# Street Fighter II Turbo AI Bot

An AI bot that plays Street Fighter II Turbo using the BizHawk emulator.

## Requirements

- Python 3.7+
- BizHawk emulator
- Street Fighter II Turbo (U) ROM
- Lua socket library
- Lua JSON library

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install BizHawk:
- Download and install BizHawk from [here](http://tasvideos.org/BizHawk.html)
- Make sure to install the Lua socket and JSON libraries

3. Configure BizHawk:
- Open BizHawk
- Load Street Fighter II Turbo (U) ROM
- Go to Tools > Lua Console
- Load the `sf2_bot.lua` script

## Project Structure

```
.
├── PythonAPI/
│   ├── bot.py              # AI bot implementation
│   ├── controller.py       # Game controller
│   ├── game_state.py       # Game state management
│   ├── buttons.py          # Button mappings
│   ├── command.py          # Command structure
│   ├── config.py           # Configuration
│   ├── logger.py           # Logging system
│   └── tests/              # Test suite
├── single-player/
│   └── Lua/
│       └── sf2_bot.lua     # Lua script for BizHawk
└── two-players/
    └── Lua/
        └── sf2_bot.lua     # Lua script for two-player mode
```

## Configuration

1. Memory Addresses:
- Edit `config.py` to adjust memory addresses if needed
- Current addresses are for Street Fighter II Turbo (U) [smc]

2. Network Settings:
- Default ports: 9998 (Player 1) and 10001 (Player 2)
- Change in both `config.py` and `sf2_bot.lua` if needed

3. Bot Behavior:
- Adjust health ratios in `config.py`
- Modify special move cooldowns
- Change combo lengths

## Running the Bot

1. Start BizHawk and load the game
2. Load the Lua script in BizHawk
3. Run the Python bot:
```bash
# For player 1
python PythonAPI/controller.py 1

# For player 2
python PythonAPI/controller.py 2
```

## Testing

Run the test suite:
```bash
python -m unittest PythonAPI/tests/test_bot.py
```

## Logging

Logs are stored in the `logs` directory:
- `bot.log`: Main log file
- Console output for real-time monitoring

## Troubleshooting

1. Connection Issues:
- Check if ports are available
- Verify BizHawk is running
- Ensure Lua script is loaded

2. Memory Reading:
- Verify memory addresses
- Check ROM version matches
- Ensure game is loaded

3. Bot Behavior:
- Adjust health ratios
- Modify reaction times
- Check special move inputs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 