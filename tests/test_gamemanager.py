# Unit tests for GameManager in Alien Enigma
# Checking if the game world sets up and runs nemesis stuff right

import unittest
from unittest.mock import Mock
from gamemanager import GameManager
import settings as config

class TestGameManager(unittest.TestCase):
    def setUp(self):
        # Get ready with fake level data and a pretend map image
        self.level_data = {
            "layers": [
                {"name": "tilemap", "data": [1, 2, 3]},
                {"name": "waypoints", "objects": [{"polyline": [{"x": 0, "y": 0}, {"x": 10, "y": 10}]}]}
            ]
        }
        self.map_image = Mock()  # Stand-in for a Pygame picture
        self.game_mgr = GameManager(self.level_data, self.map_image)

    def test_init_valid(self):
        # Make sure the game starts off okay
        self.assertEqual(self.game_mgr.level, 1)
        self.assertEqual(self.game_mgr.health, config.HEALTH)
        self.assertEqual(self.game_mgr.money, config.MONEY)
        self.assertEqual(self.game_mgr.tile_map, [])
        self.assertEqual(self.game_mgr.nemesis_list, [])

    def test_process_data(self):
        # Check if tile map and waypoints load right
        self.game_mgr.process_data()
        self.assertEqual(self.game_mgr.tile_map, [1, 2, 3])
        self.assertEqual(self.game_mgr.waypoints, [(0, 0), (10, 10)])

    def test_process_waypoints(self):
        # See if waypoints skip bad data
        waypoint_data = [{"x": 5, "y": 5}, {"x": None, "y": 10}]
        self.game_mgr.grab_waypoints(waypoint_data)
        self.assertEqual(self.game_mgr.waypoints, [(5, 5)])  # Just the good point

    def test_process_nemesis(self):
        # Test if nemesis list fills up for level 1
        self.game_mgr.process_nemesis()
        self.assertEqual(len(self.game_mgr.nemesis_list), 15)  # Should get 15 weak nemesis
        self.assertTrue(all(nemesis == "weak" for nemesis in self.game_mgr.nemesis_list))

    def test_check_level_complete(self):
        # Check if level ends when all nemesis are handled
        self.game_mgr.process_nemesis()
        self.game_mgr.killed_nemesis = 10
        self.game_mgr.missed_nemesis = 5
        self.assertTrue(self.game_mgr.check_level_complete())
        self.game_mgr.killed_nemesis = 5
        self.assertFalse(self.game_mgr.check_level_complete())

    def test_reset_level(self):
        # Make sure level clears out for a fresh start
        self.game_mgr.nemesis_list = ["weak", "medium"]
        self.game_mgr.spawned_nemesis = 2
        self.game_mgr.killed_nemesis = 1
        self.game_mgr.missed_nemesis = 1
        self.game_mgr.reset_level()
        self.assertEqual(self.game_mgr.nemesis_list, [])
        self.assertEqual(self.game_mgr.spawned_nemesis, 0)
        self.assertEqual(self.game_mgr.killed_nemesis, 0)
        self.assertEqual(self.game_mgr.missed_nemesis, 0)

    def test_draw(self):
        # Test if the map draws in the right spot
        screen = Mock()
        self.game_mgr.draw(screen)
        screen.blit.assert_called_once_with(self.map_image, (0, 0))

if __name__ == '__main__':
    unittest.main()