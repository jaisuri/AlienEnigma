# Unit tests for Nemesis class in Alien Enigma
# Testing the bad guys that walk paths and get shot by watchtowers

import unittest
from unittest.mock import Mock, patch
import pygame
from pygame.math import Vector2
from nemesis import Nemesis
import settings as config
import math

class TestNemesis(unittest.TestCase):
    def setUp(self):
        # Start Pygame and set up mocks
        pygame.init()
        # Mock game world
        self.game_world = Mock()
        self.game_world.game_speed = 1
        self.game_world.health = 100
        self.game_world.missed_nemesis = 0
        self.game_world.killed_nemesis = 0
        self.game_world.money = 0
        # Mock group for sprite
        self.group = pygame.sprite.Group()
        # Mock NEMESIS_DATA
        self.nemesis_data = {
            "basic": {"health": 100, "speed": 2}
        }
        self.patcher = patch('nemesis.NEMESIS_DATA', self.nemesis_data)
        self.patcher.start()
        # Mock config
        self.config_patch = patch('nemesis.config.KILL_REWARD', 10)
        self.config_patch.start()
        # Mock image
        self.base_image = Mock(spec=pygame.Surface)
        self.base_image.get_rect.return_value = pygame.Rect(0, 0, 32, 32)
        self.images = {"basic": self.base_image}
        # Define waypoints
        self.waypoints = [(0, 0), (100, 0), (100, 100)]
        # Create nemesis
        with patch('pygame.transform.rotate') as mock_rotate:
            rotated_image = Mock(spec=pygame.Surface)
            rotated_rect = pygame.Rect(0, 0, 32, 32)
            rotated_rect.center = (0, 0)
            rotated_image.get_rect.return_value = rotated_rect
            mock_rotate.return_value = rotated_image
            self.nemesis = Nemesis("basic", self.waypoints, self.images)
            self.group.add(self.nemesis)

    def tearDown(self):
        # Clean up Pygame and patches
        pygame.quit()
        self.patcher.stop()
        self.config_patch.stop()

    def test_init_valid(self):
        # Test nemesis sets up right
        self.assertEqual(self.nemesis.health, 100)
        self.assertEqual(self.nemesis.speed, 2)
        self.assertEqual(self.nemesis.pos, Vector2(0, 0))
        self.assertEqual(self.nemesis.target, Vector2(100, 0))
        self.assertEqual(self.nemesis.next_waypoint, 1)
        self.assertEqual(self.nemesis.angle, 0)
        self.assertEqual(self.nemesis.waypoints, self.waypoints)
        self.assertEqual(self.nemesis.base_image, self.images["basic"])
        self.assertEqual(self.nemesis.rect.center, (0, 0))
        self.assertTrue(self.nemesis.alive())

    def test_init_invalid_type(self):
        # Test bad nemesis type
        try:
            Nemesis("wrong_type", self.waypoints, self.images)
            self.fail("Should have failed with bad type")
        except:
            pass

    def test_init_empty_waypoints(self):
        # Test empty waypoints list
        try:
            Nemesis("basic", [], self.images)
            self.fail("Should have failed with empty waypoints")
        except:
            pass

    def test_init_invalid_images(self):
        # Test bad images dict
        try:
            Nemesis("basic", self.waypoints, {})
            self.fail("Should have failed with bad images")
        except:
            pass

    def test_move_toward_waypoint(self):
        # Test moving partway to next point
        self.nemesis.pos = Vector2(0, 0)
        self.nemesis.next_waypoint = 1
        self.nemesis.move(self.game_world)
        self.assertAlmostEqual(self.nemesis.pos.x, 2, places=2)  # speed = 2
        self.assertAlmostEqual(self.nemesis.pos.y, 0, places=2)
        self.assertEqual(self.nemesis.next_waypoint, 1)  # Still heading to (100, 0)
        self.assertEqual(self.nemesis.target, Vector2(100, 0))
        self.assertEqual(self.nemesis.rect.center, (2, 0))

    def test_move_snap_to_waypoint(self):
        # Test snapping to a close waypoint
        self.nemesis.pos = Vector2(99, 0)
        self.nemesis.next_waypoint = 1
        self.nemesis.move(self.game_world)
        self.assertEqual(self.nemesis.pos, Vector2(100, 0))
        self.assertEqual(self.nemesis.next_waypoint, 2)  # Move to (100, 100)
        self.assertEqual(self.nemesis.target, Vector2(100, 0))  # Target before snap
        self.assertEqual(self.nemesis.rect.center, (100, 0))

    def test_move_reach_end(self):
        # Test hitting the end of the path
        self.nemesis.next_waypoint = len(self.waypoints)  # At last waypoint
        self.nemesis.move(self.game_world)
        self.assertFalse(self.nemesis.alive())  # Nemesis killed
        self.assertEqual(self.game_world.health, 99)
        self.assertEqual(self.game_world.missed_nemesis, 1)
        self.assertEqual(self.game_world.killed_nemesis, 0)

    def test_rotate_toward_target(self):
        # Test turning to face waypoint
        self.nemesis.pos = Vector2(0, 0)
        self.nemesis.target = Vector2(100, 0)  # Right
        with patch('pygame.transform.rotate') as mock_rotate:
            rotated_image = Mock(spec=pygame.Surface)
            rotated_rect = pygame.Rect(0, 0, 32, 32)
            rotated_rect.center = (0, 0)
            rotated_image.get_rect.return_value = rotated_rect
            mock_rotate.return_value = rotated_image
            self.nemesis.rotate()
            self.assertAlmostEqual(self.nemesis.angle, 0, places=1)  # Facing right
            mock_rotate.assert_called_with(self.nemesis.base_image, 0)
            self.assertEqual(self.nemesis.rect.center, (0, 0))

    def test_rotate_no_target(self):
        # Test skipping rotation with no target
        self.nemesis.target = None
        with patch('pygame.transform.rotate') as mock_rotate:
            self.nemesis.rotate()
            mock_rotate.assert_not_called()
            self.assertEqual(self.nemesis.angle, 0)  # Unchanged

    def test_check_alive_killed(self):
        # Test nemesis dying
        self.nemesis.health = 0
        self.nemesis.check_alive(self.game_world)
        self.assertFalse(self.nemesis.alive())
        self.assertEqual(self.game_world.killed_nemesis, 1)
        self.assertEqual(self.game_world.money, 10)  # KILL_REWARD
        self.assertEqual(self.game_world.missed_nemesis, 0)

    def test_check_alive_still_alive(self):
        # Test nemesis staying alive
        self.nemesis.health = 50
        self.nemesis.check_alive(self.game_world)
        self.assertTrue(self.nemesis.alive())
        self.assertEqual(self.game_world.killed_nemesis, 0)
        self.assertEqual(self.game_world.money, 0)

    def test_update_full_cycle(self):
        # Test whole update process
        self.nemesis.pos = Vector2(0, 0)
        self.nemesis.health = 100
        with patch('pygame.transform.rotate') as mock_rotate:
            rotated_image = Mock(spec=pygame.Surface)
            rotated_rect = pygame.Rect(0, 0, 32, 32)
            rotated_rect.center = (2, 0)
            rotated_image.get_rect.return_value = rotated_rect
            mock_rotate.return_value = rotated_image
            self.nemesis.update(self.game_world)
            self.assertAlmostEqual(self.nemesis.pos.x, 2, places=2)  # Moved
            self.assertEqual(self.nemesis.target, Vector2(100, 0))  # Targeted
            self.assertTrue(self.nemesis.alive())  # Still alive

if __name__ == '__main__':
    unittest.main()