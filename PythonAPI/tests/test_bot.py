import unittest
from bot import Bot
from game_state import GameState
from player import Player
from logger import log_debug

class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot()
        self.game_state = GameState({
            'p1': {'x_coord': 100, 'y_coord': 200, 'health': 100, 'state': 0},
            'p2': {'x_coord': 300, 'y_coord': 200, 'health': 100, 'state': 0},
            'timer': 99,
            'round': 1,
            'round_started': True,
            'round_over': False
        })

    def test_update_state(self):
        """Test state update functionality"""
        self_player, opponent = self.bot.update_state(self.game_state, "1")
        self.assertEqual(self_player.x_coord, 100)
        self.assertEqual(opponent.x_coord, 300)

    def test_choose_action(self):
        """Test action selection based on distance"""
        self_player, opponent = self.bot.update_state(self.game_state, "1")
        action = self.bot.choose_action(self_player, opponent)
        self.assertIn(action, ["fireball", "move_close", "combo"])

    def test_execute_special_move(self):
        """Test special move execution"""
        self_player, _ = self.bot.update_state(self.game_state, "1")
        success = self.bot.execute_special_move(self_player, "fireball")
        self.assertTrue(success)
        self.assertEqual(self.bot.special_move_cooldown, 30)

    def test_defensive_mode(self):
        """Test defensive mode activation"""
        # Set up a situation where player 1 has low health
        self.game_state.player1.health = 30
        self.game_state.player2.health = 100
        self_player, opponent = self.bot.update_state(self.game_state, "1")
        self.assertTrue(self.bot.defensive_mode)
        self.assertFalse(self.bot.aggressive_mode)

    def test_aggressive_mode(self):
        """Test aggressive mode activation"""
        # Set up a situation where player 1 has high health
        self.game_state.player1.health = 100
        self.game_state.player2.health = 30
        self_player, opponent = self.bot.update_state(self.game_state, "1")
        self.assertTrue(self.bot.aggressive_mode)
        self.assertFalse(self.bot.defensive_mode)

    def test_run_command(self):
        """Test command execution"""
        self.bot.run_command([">", "!>", "Y", "!Y"], self.game_state.player1)
        self.assertEqual(self.bot.exe_code, 1)
        self.assertTrue(self.bot.buttn.right)
        self.assertTrue(self.bot.buttn.y)

if __name__ == '__main__':
    unittest.main() 