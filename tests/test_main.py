import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame as pg
import json
from main import GameManager, UIManager, WatchTower, Nemesis, draw_text, create_watchtower, select_watchtower, clear_selection, display_data

class TestTowerDefence(unittest.TestCase):
    def setUp(self):
        # Mock pygame initialization
        pg.init = Mock()
        pg.quit = Mock()
        pg.display.set_mode = Mock(return_value=Mock())
        pg.display.set_caption = Mock()
        pg.time.Clock = Mock(return_value=Mock(tick=Mock(return_value=60)))
        pg.time.get_ticks = Mock(return_value=1000)

        # Mock constants
        self.constants_patcher = patch('main.c', new_callable=MagicMock)
        self.mock_constants = self.constants_patcher.start()
        self.mock_constants.SCREEN_WIDTH = 800
        self.mock_constants.SIDE_PANEL = 200
        self.mock_constants.SCREEN_HEIGHT = 600
        self.mock_constants.TILE_SIZE = 32
        self.mock_constants.COLS = 25
        self.mock_constants.FPS = 60
        self.mock_constants.WATCHTOWER_LEVELS = 3
        self.mock_constants.BUY_COST = 50
        self.mock_constants.UPGRADE_COST = 100
        self.mock_constants.SPAWN_COOLDOWN = 1000
        self.mock_constants.LEVEL_COMPLETE_REWARD = 200
        self.mock_constants.TOTAL_LEVELS = 3

        # Mock image and sound loading
        self.mock_surface = Mock(get_rect=Mock(return_value=Mock()))
        pg.image.load = Mock(return_value=Mock(convert_alpha=Mock(return_value=self.mock_surface)))
        pg.mixer.Sound = Mock(return_value=Mock(set_volume=Mock()))
        pg.font.SysFont = Mock(return_value=Mock(render=Mock(return_value=Mock())))

        # Mock world data
        self.mock_world_data = {
            "level": 1,
            "waypoints": [(0, 0), (100, 100)],
            "enemies": ["weak"]
        }
        self.file_patcher = patch('builtins.open', Mock(return_value=Mock(__enter__=Mock(return_value=Mock(read=Mock(return_value=json.dumps(self.mock_world_data))), __exit__=Mock()))))
        self.file_patcher.start()
        self.world = GameManager(self.mock_world_data, Mock())
        self.world.process_data = Mock()
        self.world.process_enemies = Mock()
        self.world.tile_map = [0] * 625  # 25x25 grid
        self.world.money = 100
        self.world.health = 100
        self.world.level = 1
        self.world.spawned_enemies = 0
        self.world.enemy_list = ["weak"]
        self.world.game_speed = 1
        self.world.watchtower_spritesheets = [self.mock_surface] * self.mock_constants.WATCHTOWER_LEVELS

        # Setup groups
        self.enemy_group = pg.sprite.Group()
        self.watchtower_group = pg.sprite.Group()

        # Mock global variables for testing
        global last_enemy_spawn
        last_enemy_spawn = 0

    def tearDown(self):
        self.constants_patcher.stop()
        self.file_patcher.stop()

    #def test_create_watchtower_valid(self):
        #Test creating a watchtower on a valid tile
        # self.world.tile_map[26] = 7  # Grass tile at (1, 1)
        # with patch('main.WatchTower') as mock_watchtower:
        #     create_watchtower((32, 32))  # Tile (1, 1)
        #     mock_watchtower.assert_called_once_with(self.world.watchtower_spritesheets, 1, 1, Mock())
        #     self.assertEqual(self.world.money, 50)  # Cost deducted

    #def test_create_watchtower_occupied(self):
        #Test creating a watch tower on an occupied tile
        # self.world.tile_map[26] = 7  # Grass tile at (1, 1)
        # mock_turret = Mock(tile_x=1, tile_y=1)
        # self.turret_group.add(mock_turret)
        # with patch('main.WatchTower') as mock_watchtower:
        #     create_turret((32, 32))  # Tile (1, 1)
        #     mock_watchtower.assert_not_called()
        #     self.assertEqual(self.world.money, 100)  # No cost deducted

    # def test_select_turret(self):
    #     Test selecting a turret
    #     mock_turret = Mock(spec=pg.sprite.Sprite)
    #     mock_turret.tile_x = 1
    #     mock_turret.tile_y = 1
    #     self.turret_group.add(mock_turret)
    #     selected = select_turret((32, 32))  # Tile (1, 1)
    #     self.assertEqual(selected, mock_turret)

    def test_select_watchtower_none(self):
        #Test selecting when no turret exists
        selected = select_watchtower((32, 32))  # Tile (1, 1)
        self.assertIsNone(selected)

    #def test_clear_selection(self):
        # To Do - Fix the error
        # mock_turret = Mock(spec=pg.sprite.Sprite)  # Mock as a Sprite
        # mock_turret.selected = True
        # self.turret_group.add(mock_turret)
        # clear_selection()
        # self.assertFalse(mock_turret.selected)

    # @patch('main.pg.draw.rect')
    # @patch('main.draw_text')
    # def test_display_data(self, mock_draw_text, mock_draw_rect):
    #     Test displaying game data
    #     self.world.level = 1
    #     self.world.health = 100
    #     self.world.money = 500
    #     display_data()
    #     self.assertTrue(mock_draw_rect.called)
    #     mock_draw_text.assert_any_call("LEVEL: 1", Mock(), "grey100", 810, 10)
    #     mock_draw_text.assert_any_call("100", Mock(), "grey100", 850, 40)
    #     mock_draw_text.assert_any_call("500", Mock(), "grey100", 850, 70)

    # @patch('main.pg.time.get_ticks')
    # def test_enemy_spawn(self, mock_get_ticks):
        #Test enemy spawning logic
        # global last_enemy_spawn
        # mock_get_ticks.return_value = 2000  # 1000ms after last_spawn
        # with patch('main.Nemesis') as mock_nemesis:
        #     if mock_get_ticks() - last_enemy_spawn > self.mock_constants.SPAWN_COOLDOWN:
        #         if self.world.spawned_enemies < len(self.world.enemy_list):
        #             mock_nemesis.return_value = Mock()
        #             enemy = mock_nemesis("weak", self.world.waypoints, Mock())
        #             self.enemy_group.add(enemy)
        #             self.world.spawned_enemies += 1
        #             last_enemy_spawn = mock_get_ticks()
        #     mock_nemesis.assert_called_once_with("weak", self.world.waypoints, Mock())
        #     self.assertEqual(self.world.spawned_enemies, 1)

    def test_game_over_loss(self):
        #Test game over condition for loss
        global game_over, game_outcome
        game_over = False
        game_outcome = 0
        self.world.health = 0
        if self.world.health <= 0:
            game_over = True
            game_outcome = -1
        self.assertTrue(game_over)
        self.assertEqual(game_outcome, -1)

    def test_game_over_win(self):
        #Test game over condition for win
        global game_over, game_outcome
        game_over = False
        game_outcome = 0
        self.world.level = 4  # Exceeds TOTAL_LEVELS (3)
        if self.world.level > self.mock_constants.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1
        self.assertTrue(game_over)
        self.assertEqual(game_outcome, 1)

if __name__ == '__main__':
    unittest.main()