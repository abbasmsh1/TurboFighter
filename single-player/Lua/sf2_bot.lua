-- Street Fighter II Turbo Bot Lua Script
local socket = require("socket")
local json = require("json")

-- Configuration
local HOST = "127.0.0.1"
local PORT_P1 = 9998
local PORT_P2 = 10001
local BUFFER_SIZE = 4096

-- Memory addresses
local MEMORY = {
    PLAYER1 = {
        X_POS = 0x7E0F80,
        Y_POS = 0x7E0F82,
        HEALTH = 0x7E0F84,
        STATE = 0x7E0F86
    },
    PLAYER2 = {
        X_POS = 0x7E0F88,
        Y_POS = 0x7E0F8A,
        HEALTH = 0x7E0F8C,
        STATE = 0x7E0F8E
    },
    GAME = {
        TIMER = 0x7E0F90,
        ROUND = 0x7E0F92,
        ROUND_STATE = 0x7E0F94
    }
}

-- Initialize socket
local client = socket.tcp()
local connected = false

-- Function to read memory
local function read_memory(address, size)
    return memory.readbyte(address, size)
end

-- Function to get button states
local function get_button_states(player)
    local buttons = joypad.get(player)
    return {
        up = buttons.Up or false,
        down = buttons.Down or false,
        left = buttons.Left or false,
        right = buttons.Right or false,
        y = buttons.Y or false,
        b = buttons.B or false,
        a = buttons.A or false,
        x = buttons.X or false,
        l = buttons.L or false,
        r = buttons.R or false
    }
end

-- Function to get game state
local function get_game_state()
    local state = {
        p1 = {
            x_coord = read_memory(MEMORY.PLAYER1.X_POS, 2),
            y_coord = read_memory(MEMORY.PLAYER1.Y_POS, 2),
            health = read_memory(MEMORY.PLAYER1.HEALTH, 2),
            state = read_memory(MEMORY.PLAYER1.STATE, 1),
            buttons = get_button_states(1)
        },
        p2 = {
            x_coord = read_memory(MEMORY.PLAYER2.X_POS, 2),
            y_coord = read_memory(MEMORY.PLAYER2.Y_POS, 2),
            health = read_memory(MEMORY.PLAYER2.HEALTH, 2),
            state = read_memory(MEMORY.PLAYER2.STATE, 1),
            buttons = get_button_states(2)
        },
        timer = read_memory(MEMORY.GAME.TIMER, 2),
        round = read_memory(MEMORY.GAME.ROUND, 1),
        round_started = read_memory(MEMORY.GAME.ROUND_STATE, 1) == 1,
        round_over = read_memory(MEMORY.GAME.ROUND_STATE, 1) == 2
    }
    return state
end

-- Function to execute commands
local function execute_commands(commands)
    for _, cmd in ipairs(commands) do
        if cmd.type == "buttons" then
            joypad.set(1, cmd.p1)
            joypad.set(2, cmd.p2)
        end
    end
end

-- Main loop
while true do
    if not connected then
        -- Try to connect
        client:settimeout(1)
        local success, err = client:connect(HOST, PORT_P1)
        if success then
            connected = true
            print("Connected to Python bot")
        else
            print("Connection failed: " .. err)
            emu.frameadvance()
        end
    else
        -- Get game state
        local game_state = get_game_state()
        
        -- Send game state to Python bot
        local success, err = client:send(json.encode(game_state))
        if not success then
            print("Send failed: " .. err)
            connected = false
            client:close()
            emu.frameadvance()
        end
        
        -- Receive commands from Python bot
        local data, err = client:receive(BUFFER_SIZE)
        if data then
            local commands = json.decode(data)
            execute_commands(commands)
        elseif err ~= "timeout" then
            print("Receive failed: " .. err)
            connected = false
            client:close()
        end
    end
    
    emu.frameadvance()
end 