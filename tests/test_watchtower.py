import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame as pg
import math
from watchtower import WatchTower  # Adjust import if needed

class TestWatchTower(unittest.TestCase):
    def setUp(self):
        # Mock pygame sprite initialization properly
        pg.sprite.Sprite.__init__ = lambda self: setattr(self, '_Sprite__g', {})

        # Mock constants
        self.constants_patcher = patch('watchtower.c', new_callable=MagicMock)
        self.mock_constants = self.constants_patcher.start()
        self.mock_constants.TILE_SIZE = 32
        self.mock_constants.ANIMATION_STEPS = 4
        self.mock_constants.ANIMATION_DELAY = 100
        self.mock_constants.DAMAGE = 10

        # Mock WATCHTOWER_INFO
        self.turret_data_patcher = patch('watchtower.WATCHTOWER_INFO', [
            {"range": 100, "cooldown": 1000},
            {"range": 150, "cooldown": 800},
            {"range": 200, "cooldown": 600},
            {"range": 250, "cooldown": 400}  # Level 4 (initial)
        ])
        self.turret_data_patcher.start()

        # Mock sprite sheet and sound
        self.mock_surface = Mock(spec=pg.Surface)
        self.mock_surface.get_height = Mock(return_value=32)
        self.mock_surface.subsurface = Mock(return_value=self.mock_surface)
        self.mock_surface.get_rect = Mock(return_value=Mock(center=(0, 0)))
        self.sprite_sheets = [self.mock_surface] * 4
        self.shot_fx = Mock(play=Mock())

        # Mock pygame surface-related methods
        self.surface_patcher = patch('watchtower.pg.Surface', return_value=self.mock_surface)
        self.rotate_patcher = patch('watchtower.pg.transform.rotate', return_value=self.mock_surface)
        self.circle_patcher = patch('watchtower.pg.draw.circle')
        self.time_patcher = patch('watchtower.pg.time.get_ticks', return_value=1000)
        self.surface_patcher.start()
        self.rotate_patcher.start()
        self.circle_patcher.start()
        self.time_patcher.start()

        # Create fresh WatchTower instance for each test
        self.tower = WatchTower(self.sprite_sheets, 2, 3, self.shot_fx)

        # Mock enemy for targeting tests
        self.enemy = Mock(health=50, pos=[100, 100])

    def tearDown(self):
        self.constants_patcher.stop()
        self.turret_data_patcher.stop()
        self.surface_patcher.stop()
        self.rotate_patcher.stop()
        self.circle_patcher.stop()
        self.time_patcher.stop()

    def test_init_valid(self):
        #Test initialization with valid parameters
        self.assertEqual(self.tower.upgrade_level, 4)
        self.assertEqual(self.tower.range, 250)
        self.assertEqual(self.tower.cooldown, 400)
        self.assertFalse(self.tower.selected)
        self.assertIsNone(self.tower.target)
        self.assertEqual(self.tower.tile_x, 2)
        self.assertEqual(self.tower.tile_y, 3)
        self.assertEqual(self.tower.x, (2 + 0.5) * 32)  # 80
        self.assertEqual(self.tower.y, (3 + 0.5) * 32)  # 112

    def test_init_invalid_spritesheet(self):
        #Test initialization with invalid sprite sheets
        with self.assertRaises(TypeError):
            WatchTower(None, 1, 1, self.shot_fx)

    def test_load_images(self):
        #Test loading images from sprite sheet
        animation_list = self.tower.load_images(self.sprite_sheets[0])  # Use the first sprite sheet from the list
        self.assertEqual(len(animation_list), 4)  # ANIMATION_STEPS
        self.sprite_sheets[0].subsurface.assert_called()

    def test_update_with_target(self):
        #Test update method when tower has a target
        self.tower.target = self.enemy
        with patch.object(self.tower, 'play_animation') as mock_play:
            self.tower.update(Mock(), Mock(game_speed=1))
            mock_play.assert_called_once()

    def test_update_no_target(self):
        #Test update method when no target and cooldown passed
        pg.time.get_ticks.return_value = 2000  # 1000ms after last_shot
        enemy_group = Mock(__iter__=Mock(return_value=[self.enemy]))
        with patch.object(self.tower, 'pick_target') as mock_pick:
            self.tower.update(enemy_group, Mock(game_speed=1))
            mock_pick.assert_called_once_with(enemy_group)

    def test_pick_target_in_range(self):
        #Test picking a target within range
        enemy_group = [self.enemy]
        self.tower.x = 90
        self.tower.y = 90  # Distance ~14.14 < 250 (range)
        self.tower.pick_target(enemy_group)
        self.assertEqual(self.tower.target, self.enemy)
        self.assertEqual(self.enemy.health, 40)  # 50 - DAMAGE (10)
        self.shot_fx.play.assert_called_once()
        self.assertAlmostEqual(self.tower.angle, math.degrees(math.atan2(-10, 10)), places=5)

    def test_pick_target_out_of_range(self):
        #Test picking a target out of range
        self.enemy.pos = [400, 400]  # Distance > 250
        enemy_group = [self.enemy]
        self.tower.pick_target(enemy_group)
        self.assertIsNone(self.tower.target)
        self.shot_fx.play.assert_not_called()

    def test_play_animation(self):
        #Test animation playback
        pg.time.get_ticks.return_value = 1200  # 200ms after update_time (1000)
        self.tower.frame_index = 0
        self.tower.play_animation()
        self.assertEqual(self.tower.frame_index, 1)  # Advances frame
        self.assertEqual(self.tower.update_time, 1200)

    def test_play_animation_complete(self):
        #Test animation completion resets target
        self.tower.frame_index = 3  # Last frame
        self.tower.target = self.enemy
        pg.time.get_ticks.return_value = 1200
        self.tower.play_animation()
        self.assertEqual(self.tower.frame_index, 0)  # Resets to idle
        self.assertIsNone(self.tower.target)
        self.assertEqual(self.tower.last_shot, 1200)

    def test_draw_selected(self):
        #Test drawing with range circle when selected
        surface = Mock()
        self.tower.selected = True
        self.tower.draw(surface)
        self.assertEqual(surface.blit.call_count, 2)  # Image + range circle

if __name__ == '__main__':
    unittest.main()