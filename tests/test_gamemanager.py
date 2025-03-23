import unittest
import pygame as pg
from gamemanager import GameManager
from unittest.mock import patch

# Mock constants and nemesis spawn data
class MockConstants:
    HEALTH = 100
    MONEY = 200

NEMESIS_SPAWN_DATA = [
    {"weak": 3, "strong": 2},  # Level 1
    {"weak": 5, "strong": 3}   # Level 2
]

# Sample level data
SAMPLE_LEVEL_DATA = {
    "layers": [
        {"name": "tilemap", "data": [0, 1, 2, 3]},
        {"name": "waypoints", "objects": [{"polyline": [{"x": 0, "y": 0}, {"x": 50, "y": 50}]}]}
    ]
}

class TestGameManager(unittest.TestCase):
    def setUp(self):
        # Initialize Pygame and mock resources
        try:
            pg.init()
            self.map_image = pg.Surface((1000, 600))
            self.map_image.fill((0, 255, 0))  # Green map
            self.screen = pg.display.set_mode((1000, 600), pg.HIDDEN)
        except pg.error as e:
            self.skipTest(f"Skipping test due to Pygame init failure: {e}")

    def tearDown(self):
        # Clean up Pygame
        try:
            pg.quit()
        except Exception as e:
            print(f"Warning: Failed to quit Pygame in tearDown: {e}")

    def test_init_valid(self):
        # Test GameManager initialization
        with patch('gamemanager.c', MockConstants):
            world = GameManager(SAMPLE_LEVEL_DATA, self.map_image)
            self.assertEqual(world.level, 1)
            self.assertEqual(world.health, 100)
            self.assertEqual(world.money, 200)
            self.assertEqual(world.image, self.map_image)

    def test_process_data(self):
        # Test processing level data
        with patch('gamemanager.c', MockConstants):
            world = GameManager(SAMPLE_LEVEL_DATA, self.map_image)
            world.process_data()
            self.assertEqual(world.tile_map, [0, 1, 2, 3])
            self.assertEqual(world.waypoints, [(0, 0), (50, 50)])

    def test_process_waypoints(self):
        # Test waypoint extraction
        with patch('gamemanager.c', MockConstants):
            world = GameManager(SAMPLE_LEVEL_DATA, self.map_image)
            world.process_waypoints([{"x": 10, "y": 20}, {"x": 30, "y": 40}])
            self.assertEqual(world.waypoints, [(10, 20), (30, 40)])

    def test_process_enemies(self):
        # Test enemy list generation and shuffling
        with patch('gamemanager.c', MockConstants), patch('gamemanager.NEMESIS_SPAWN_DATA', NEMESIS_SPAWN_DATA):
            world = GameManager(SAMPLE_LEVEL_DATA, self.map_image)
            world.process_enemies()
            self.assertEqual(len(world.enemy_list), 5)  # 3 weak + 2 strong
            self.assertTrue(all(e in ["weak", "strong"] for e in world.enemy_list))

    def test_check_level_complete(self):
        # Test level completion check
        with patch('gamemanager.c', MockConstants), patch('gamemanager.NEMESIS_SPAWN_DATA', NEMESIS_SPAWN_DATA):
            world = GameManager(SAMPLE_LEVEL_DATA, self.map_image)
            world.process_enemies()
            world.killed_enemies = 3
            world.missed_enemies = 2
            self.assertTrue(world.check_level_complete())

    def test_reset_level(self):
        # Test level reset
        with patch('gamemanager.c', MockConstants):
            world = GameManager(SAMPLE_LEVEL_DATA, self.map_image)
            world.spawned_enemies = 5
            world.killed_enemies = 3
            world.missed_enemies = 2
            world.reset_level()
            self.assertEqual(world.spawned_enemies, 0)
            self.assertEqual(world.killed_enemies, 0)
            self.assertEqual(world.missed_enemies, 0)
            self.assertEqual(world.enemy_list, [])

    def test_draw(self):
        # Test drawing the world
        with patch('gamemanager.c', MockConstants):
            world = GameManager(SAMPLE_LEVEL_DATA, self.map_image)
            world.draw(self.screen)
            self.assertEqual(self.screen.get_at((0, 0)), pg.Color(0, 255, 0, 255))

if __name__ == "__main__":
    unittest.main()