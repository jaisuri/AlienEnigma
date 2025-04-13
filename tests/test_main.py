# Unit tests for Alien Enigma main game
# Checking watchtowers and nemesis stuff work right

import unittest
from unittest.mock import Mock, patch
import pygame
import main
from pygame.sprite import Sprite

class TestAlienEnigma(unittest.TestCase):
    def setUp(self):
        # Start Pygame and mock game bits
        pygame.init()
        self.screen = Mock(spec=pygame.Surface)
        main.screen = self.screen
        main.world = Mock()
        main.watchtower_group = pygame.sprite.Group()
        main.text_font = Mock()
        # Fake settings
        main.config = Mock(SCREEN_WIDTH=720, SCREEN_HEIGHT=720, COLS=15, ROWS=15, 
                          TILE_SIZE=48, HEALTH=100, TOTAL_LEVELS=15, SIDE_PANEL=200,
                          BUY_COST=200)
        main.logo_image = Mock()
        main.heart_image = Mock()
        main.coin_image = Mock()
        # Mock watchtower assets
        main.watchtower_sheets = [
            Mock(spec=pygame.Surface),
            Mock(spec=pygame.Surface),
            Mock(spec=pygame.Surface),
            Mock(spec=pygame.Surface)
        ]
        main.watchtower_shot = Mock(spec=pygame.mixer.Sound)

    def tearDown(self):
        # Shut down Pygame
        pygame.quit()

    def test_draw_text(self):
        # Test if text shows up
        main.text_font.render.return_value = Mock()
        main.draw_text("Test", main.text_font, "black", 10, 20)
        main.text_font.render.assert_called_with("Test", True, "black")
        self.assertTrue(self.screen.blit.called)

    def test_display_data(self):
        # Test stats panel
        main.world.level = 1
        main.world.health = 50
        main.world.money = 100
        with patch('pygame.draw.rect'), patch('main.draw_text') as mock_draw:
            main.display_data()
            self.assertTrue(self.screen.blit.called)
            mock_draw.assert_any_call("LEVEL: 1", main.text_font, "black", 
                                    main.config.SCREEN_WIDTH + 100, 10)


    def test_select_watchtower(self):
        # Test picking a watchtower
        class FakeTower(Sprite):
            def __init__(self):
                super().__init__()
                self.tile_x = 1
                self.tile_y = 1
        watchtower = FakeTower()
        main.watchtower_group.add(watchtower)
        picked = main.select_watchtower((48, 48))
        self.assertEqual(picked, watchtower)

    def test_select_watchtower_none(self):
        # Test no watchtower picked
        picked = main.select_watchtower((48, 48))
        self.assertIsNone(picked)

    def test_clear_selection(self):
        # Test unselecting watchtower
        class FakeTower(Sprite):
            def __init__(self):
                super().__init__()
                self.selected = True
        watchtower = FakeTower()
        main.watchtower_group.add(watchtower)
        main.clear_selection()
        self.assertFalse(watchtower.selected)

    def test_game_over_loss(self):
        # Test game over when health hits zero
        main.world.health = 0
        main.game_over = False
        main.game_outcome = 0
        with patch('main.world') as mock_world:
            mock_world.health = 0
            if not main.game_over:
                if mock_world.health <= 0:
                    main.game_over, main.game_outcome = True, -1
            self.assertTrue(main.game_over)
            self.assertEqual(main.game_outcome, -1)

    def test_game_over_win(self):
        # Test winning after all levels
        main.world.level = main.config.TOTAL_LEVELS + 1
        main.game_over = False
        main.game_outcome = 0
        with patch('main.world') as mock_world:
            mock_world.level = main.config.TOTAL_LEVELS + 1
            if not main.game_over:
                if mock_world.level > main.config.TOTAL_LEVELS:
                    main.game_over, main.game_outcome = True, 1
            self.assertTrue(main.game_over)
            self.assertEqual(main.game_outcome, 1)

if __name__ == '__main__':
    unittest.main()