# Unit tests for WatchTower class in Alien Enigma
# Testing watchtowers that zap nemesis with cool animations

import unittest
from unittest.mock import Mock, patch
import pygame
from watchtower import WatchTower
import settings as config
import math

class TestWatchTower(unittest.TestCase):
    def setUp(self):
        # Start Pygame and set up mocks
        pygame.init()
        # Mock sprite sheet
        self.sprite_sheet = Mock(spec=pygame.Surface)
        self.sprite_sheet.get_height.return_value = 32
        frame_surface = Mock(spec=pygame.Surface)
        frame_surface.get_rect.return_value = pygame.Rect(0, 0, 32, 32)
        self.sprite_sheet.subsurface.return_value = frame_surface
        self.sprite_sheets = [self.sprite_sheet]
        # Mock shot sound
        self.shot_sound = Mock()
        # Mock WATCHTOWER_INFO
        self.watchtower_info = [
            {"range": 100, "cooldown": 1000},
            {"range": 150, "cooldown": 800}
        ]
        self.patcher = patch('watchtower.WATCHTOWER_INFO', self.watchtower_info)
        self.patcher.start()
        # Mock config constants
        self.config_patch = patch.multiple('watchtower.config',
            TILE_SIZE=64, ANIMATION_STEPS=4, ANIMATION_DELAY=100, DAMAGE=10)
        self.config_patch.start()
        # Mock screen
        self.screen = Mock(spec=pygame.Surface)
        # Mock game world
        self.game_world = Mock()
        self.game_world.game_speed = 1
        # Create watchtower at tile (2, 3)
        with patch('pygame.transform.rotate') as mock_rotate:
            rotated_surface = Mock(spec=pygame.Surface)
            rotated_rect = pygame.Rect(0, 0, 32, 32)
            rotated_rect.center = (2.5 * 64, 3.5 * 64)
            rotated_surface.get_rect.return_value = rotated_rect
            mock_rotate.return_value = rotated_surface
            self.watchtower = WatchTower(self.sprite_sheets, 2, 3, self.shot_sound)
            # Mock range image for consistency
            self.watchtower.range_image = Mock(spec=pygame.Surface)
            self.watchtower.range_image.get_size.return_value = (200, 200)
            self.watchtower.range_rect = pygame.Rect(0, 0, 200, 200)
            self.watchtower.range_rect.center = (self.watchtower.x, self.watchtower.y)

    def tearDown(self):
        # Clean up Pygame and patches
        pygame.quit()
        self.patcher.stop()
        self.config_patch.stop()

    def test_init_valid(self):
        # Test watchtower sets up right
        self.assertEqual(self.watchtower.level, 1)
        self.assertEqual(self.watchtower.range, 100)
        self.assertEqual(self.watchtower.cooldown, 1000)
        self.assertEqual(self.watchtower.tile_x, 2)
        self.assertEqual(self.watchtower.tile_y, 3)
        self.assertEqual(self.watchtower.x, 2.5 * 64)
        self.assertEqual(self.watchtower.y, 3.5 * 64)
        self.assertFalse(self.watchtower.selected)
        self.assertIsNone(self.watchtower.target)
        self.assertEqual(self.watchtower.angle, 90)
        self.assertEqual(self.watchtower.sprite_sheets, self.sprite_sheets)
        self.assertEqual(self.watchtower.frame_index, 0)
        self.assertEqual(self.watchtower.rect.center, (2.5 * 64, 3.5 * 64))

    def test_init_invalid_sprites(self):
        # Test with empty sprite sheets
        try:
            WatchTower([], 2, 3, self.shot_sound)
            self.fail("Should have failed with empty sprites")
        except:
            pass

    def test_init_invalid_level(self):
        # Test with bad WATCHTOWER_INFO
        bad_info = []
        with patch('watchtower.WATCHTOWER_INFO', bad_info):
            try:
                WatchTower(self.sprite_sheets, 2, 3, self.shot_sound)
                self.fail("Should have failed with bad level data")
            except:
                pass

    def test_load_frames(self):
        # Test cutting up sprite sheet
        frames = self.watchtower._load_frames(self.sprite_sheet)
        self.assertEqual(len(frames), 4)  # ANIMATION_STEPS
        self.sprite_sheet.subsurface.assert_called_with(3 * 32, 0, 32, 32)

    def test_load_frames_invalid_sheet(self):
        # Test bad sprite sheet
        bad_sheet = Mock()
        bad_sheet.get_height.side_effect = pygame.error
        frames = self.watchtower._load_frames(bad_sheet)
        self.assertEqual(frames, [])

    def test_make_range_circle(self):
        # Test range circle creation
        with patch('pygame.Surface') as mock_surface, \
             patch('pygame.draw.circle') as mock_draw:
            range_surface = mock_surface.return_value
            range_rect = pygame.Rect(0, 0, 200, 200)
            range_rect.center = (self.watchtower.x, self.watchtower.y)
            range_surface.get_rect.return_value = range_rect
            self.watchtower._make_range_circle()
            mock_surface.assert_called_with((200, 200))
            range_surface.fill.assert_called_with((0, 0, 0))
            range_surface.set_colorkey.assert_called_with((0, 0, 0))
            mock_draw.assert_called_with(
                range_surface,
                "grey100",
                (self.watchtower.range, self.watchtower.range),
                self.watchtower.range
            )
            range_surface.set_alpha.assert_called_with(100)

    def test_find_nemesis_in_range(self):
        # Test picking a nemesis to shoot
        nemesis = Mock(spec=pygame.sprite.Sprite)
        nemesis.health = 50
        nemesis.pos = [self.watchtower.x + 50, self.watchtower.y]  # Within 100 range
        nemesis.add_internal = Mock()
        nemesis.remove_internal = Mock()
        nemesis_group = pygame.sprite.Group()
        nemesis_group.add(nemesis)
        self.watchtower.find_nemesis(nemesis_group)
        self.assertEqual(self.watchtower.target, nemesis)
        self.assertAlmostEqual(self.watchtower.angle, 0, places=1)  # Facing right
        self.assertEqual(nemesis.health, 40)  # 50 - DAMAGE
        self.shot_sound.play.assert_called_once()

    def test_find_nemesis_out_of_range(self):
        # Test no nemesis in range
        nemesis = Mock(spec=pygame.sprite.Sprite)
        nemesis.health = 50
        nemesis.pos = [self.watchtower.x + 200, self.watchtower.y]  # Too far
        nemesis.add_internal = Mock()
        nemesis.remove_internal = Mock()
        nemesis_group = pygame.sprite.Group()
        nemesis_group.add(nemesis)
        self.watchtower.find_nemesis(nemesis_group)
        self.assertIsNone(self.watchtower.target)
        self.assertEqual(self.shot_sound.play.call_count, 0)

    def test_animate(self):
        # Test animation when shooting
        self.watchtower.target = Mock()
        self.watchtower.frame_index = 0
        with patch('pygame.time.get_ticks', return_value=1000):
            self.watchtower.frame_time = 850  # 150ms ago
            self.watchtower.animate()
            self.assertEqual(self.watchtower.frame_index, 1)
            self.assertEqual(self.watchtower.base_image, self.watchtower.frames[1])

    def test_animate_complete(self):
        # Test finishing animation
        self.watchtower.target = Mock()
        self.watchtower.frame_index = 3  # Last frame
        with patch('pygame.time.get_ticks', return_value=1000):
            self.watchtower.frame_time = 850
            self.watchtower.animate()
            self.assertEqual(self.watchtower.frame_index, 0)  # Reset
            self.assertIsNone(self.watchtower.target)
            self.assertEqual(self.watchtower.last_shot, 1000)

    def test_update_with_target(self):
        # Test update when shooting
        self.watchtower.target = Mock()
        nemesis_group = Mock(spec=pygame.sprite.Group)
        with patch.object(self.watchtower, 'animate') as mock_animate:
            self.watchtower.update(nemesis_group, self.game_world)
            mock_animate.assert_called_once()

    def test_update_no_target_ready(self):
        # Test update when cooled down
        self.watchtower.last_shot = 0
        nemesis_group = Mock(spec=pygame.sprite.Group)
        with patch('pygame.time.get_ticks', return_value=2000), \
             patch.object(self.watchtower, 'find_nemesis') as mock_find:
            self.watchtower.update(nemesis_group, self.game_world)
            mock_find.assert_called_with(nemesis_group)

    def test_upgrade(self):
        # Test leveling up watchtower
        with patch('pygame.transform.rotate') as mock_rotate, \
             patch.object(self.watchtower, '_make_range_circle') as mock_range:
            rotated_surface = Mock(spec=pygame.Surface)
            rotated_surface.get_rect.return_value = pygame.Rect(0, 0, 32, 32)
            mock_rotate.return_value = rotated_surface
            self.watchtower.upgrade()
            self.assertEqual(self.watchtower.level, 2)
            self.assertEqual(self.watchtower.range, 150)
            self.assertEqual(self.watchtower.cooldown, 800)
            self.assertEqual(len(self.watchtower.frames), 4)

    def test_upgrade_max_level(self):
        # Test upgrading past max
        self.watchtower.level = 2
        self.watchtower.upgrade()
        self.assertEqual(self.watchtower.level, 3)  # Increments but fails
        self.assertEqual(self.watchtower.range, 100)  # Stays at level 1
        self.assertEqual(self.watchtower.cooldown, 1000)

    def test_draw_selected(self):
        # Test drawing with range circle
        self.watchtower.selected = True
        with patch('pygame.transform.rotate') as mock_rotate:
            rotated_surface = Mock(spec=pygame.Surface)
            rotated_rect = pygame.Rect(0, 0, 32, 32)
            rotated_rect.center = (self.watchtower.x, self.watchtower.y)
            rotated_surface.get_rect.return_value = rotated_rect
            mock_rotate.return_value = rotated_surface
            self.watchtower.draw(self.screen)
            self.screen.blit.assert_any_call(self.watchtower.image, self.watchtower.rect)
            self.screen.blit.assert_any_call(self.watchtower.range_image, self.watchtower.range_rect)

    def test_draw_not_selected(self):
        # Test drawing without range circle
        self.watchtower.selected = False
        with patch('pygame.transform.rotate') as mock_rotate:
            rotated_surface = Mock(spec=pygame.Surface)
            rotated_rect = pygame.Rect(0, 0, 32, 32)
            rotated_rect.center = (self.watchtower.x, self.watchtower.y)
            rotated_surface.get_rect.return_value = rotated_rect
            mock_rotate.return_value = rotated_surface
            self.watchtower.draw(self.screen)
            self.screen.blit.assert_called_with(self.watchtower.image, self.watchtower.rect)
            self.assertEqual(self.screen.blit.call_count, 1)  # No range circle

if __name__ == '__main__':
    unittest.main()