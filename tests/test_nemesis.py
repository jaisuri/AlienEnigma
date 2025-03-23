import unittest
import pygame as pg
from pygame.math import Vector2
from nemesis import Nemesis
from unittest.mock import patch

# Mock constants and nemesis data for testing
class MockConstants:
    KILL_REWARD = 10

class MockGameManager:
    def __init__(self):
        self.health = 100
        self.money = 0
        self.killed_enemies = 0
        self.missed_enemies = 0
        self.game_speed = 1

NEMESIS_DATA = {
    "weak": {"health": 50, "speed": 2},
    "strong": {"health": 100, "speed": 1}
}

class TestNemesis(unittest.TestCase):
    def setUp(self):
        # Initialize Pygame and mock resources for tests
        try:
            pg.init()
            self.screen = pg.display.set_mode((1000, 600), pg.HIDDEN)  # Headless mode
            self.image = pg.Surface((32, 32))
            self.image.fill((255, 0, 0))  # Red sprite
            self.images = {"weak": self.image, "strong": self.image}
            self.world = MockGameManager()
        except pg.error as e:
            self.skipTest(f"Skipping test due to Pygame init failure: {e}")

    def tearDown(self):
        # Clean up Pygame after each test
        try:
            pg.quit()
        except Exception as e:
            print(f"Warning: Failed to quit Pygame in tearDown: {e}")

    def test_init_valid(self):
        # Test Nemesis initialization with valid parameters
        waypoints = [(0, 0), (50, 50)]
        nemesis = Nemesis("weak", waypoints, self.images)
        self.assertEqual(nemesis.pos, Vector2(0, 0))
        self.assertEqual(nemesis.health, 10)
        self.assertEqual(nemesis.speed, 2)
        self.assertEqual(nemesis.target_waypoint, 1)
        self.assertTrue(hasattr(nemesis, "image"))

    def test_move_along_path(self):
        # Test movement along waypoints
        waypoints = [(0, 0), (50, 50)]
        nemesis = Nemesis("weak", waypoints, self.images)
        nemesis.move(self.world)
        self.assertNotEqual(nemesis.pos, Vector2(0, 0))
        self.assertTrue(nemesis.pos.x > 0 and nemesis.pos.y > 0)

    def test_move_reach_end(self):
        # Test reaching end of path
        waypoints = [(0, 0), (2, 2)]  # Short path, speed = 2
        nemesis = Nemesis("weak", waypoints, self.images)
        nemesis.move(self.world)  # Reach (2, 2)
        nemesis.move(self.world)  # Beyond end
        self.assertFalse(nemesis.alive())
        self.assertEqual(self.world.health, 100)
        self.assertEqual(self.world.missed_enemies, 0)

    def test_rotate(self):
        # Test rotation towards next waypoint
        waypoints = [(0, 0), (50, 0)]  # Horizontal path
        nemesis = Nemesis("weak", waypoints, self.images)
        nemesis.rotate()
        self.assertEqual(nemesis.angle, 0)  # Facing right

    def test_check_alive_dead(self):
        # Test check_alive when health is depleted
        waypoints = [(0, 0), (50, 50)]
        nemesis = Nemesis("weak", waypoints, self.images)
        nemesis.health = 0
        with patch('nemesis.c', MockConstants):
            nemesis.check_alive(self.world)
        self.assertFalse(nemesis.alive())
        self.assertEqual(self.world.killed_enemies, 1)
        self.assertEqual(self.world.money, 10)

    def test_update_full_cycle(self):
        # Test full update cycle
        waypoints = [(0, 0), (50, 50)]
        nemesis = Nemesis("weak", waypoints, self.images)
        nemesis.update(self.world)
        self.assertNotEqual(nemesis.pos, Vector2(0, 0))
        self.assertNotEqual(nemesis.angle, 0)
        self.assertFalse(nemesis.alive())

if __name__ == "__main__":
    unittest.main()