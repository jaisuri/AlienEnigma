# Unit tests for UIManager class in Alien Enigma
# Testing buttons for buying watchtowers and starting nemesis waves

import unittest
from unittest.mock import Mock, patch
import pygame
from uimanager import UIManager

class TestUIManager(unittest.TestCase):
    def setUp(self):
        # Start Pygame and set up mocks
        pygame.init()
        # Mock button image
        self.button_image = Mock(spec=pygame.Surface)
        self.button_rect = pygame.Rect(50, 50, 100, 40)
        self.button_image.get_rect.return_value = self.button_rect
        # Mock screen
        self.screen = Mock(spec=pygame.Surface)
        # Create UIManager instances
        self.ui_button = UIManager(50, 50, self.button_image, False)
        self.ui_one_shot = UIManager(50, 50, self.button_image, True)

    def tearDown(self):
        # Clean up Pygame
        pygame.quit()

    def test_init_valid(self):
        # Test button sets up right
        self.assertEqual(self.ui_button.image, self.button_image)
        self.assertEqual(self.ui_button.rect.topleft, (50, 50))
        self.assertEqual(self.ui_button.rect.x, 50)
        self.assertEqual(self.ui_button.rect.y, 50)
        self.assertFalse(self.ui_button.is_clicked)
        self.assertFalse(self.ui_button.one_shot)
        self.assertTrue(self.ui_one_shot.one_shot)

    def test_init_invalid_image(self):
        # Test with bad image
        try:
            UIManager(50, 50, None, False)
            self.fail("Should have failed with bad image")
        except:
            pass

    def test_draw_no_click(self):
        # Test drawing without clicking
        with patch('pygame.mouse.get_pos', return_value=(0, 0)), \
             patch('pygame.mouse.get_pressed', return_value=(0, 0, 0)):
            result = self.ui_button.draw(self.screen)
            self.assertFalse(result)
            self.assertFalse(self.ui_button.is_clicked)
            self.screen.blit.assert_called_with(self.ui_button.image, self.ui_button.rect)

    def test_draw_click(self):
        # Test clicking the button
        with patch('pygame.mouse.get_pos', return_value=(60, 60)), \
             patch('pygame.mouse.get_pressed', return_value=(1, 0, 0)):
            result = self.ui_button.draw(self.screen)
            self.assertTrue(result)
            self.screen.blit.assert_called_with(self.ui_button.image, self.ui_button.rect)

    def test_draw_one_shot_clicked(self):
        # Test one-shot button gets clicked
        with patch('pygame.mouse.get_pos', return_value=(60, 60)), \
             patch('pygame.mouse.get_pressed', return_value=(1, 0, 0)):
            result = self.ui_one_shot.draw(self.screen)
            self.assertTrue(result)
            self.screen.blit.assert_called_with(self.ui_one_shot.image, self.ui_one_shot.rect)

    def test_draw_click_release(self):
        # Test button resets after releasing mouse
        with patch('pygame.mouse.get_pos', return_value=(60, 60)), \
             patch('pygame.mouse.get_pressed', return_value=(1, 0, 0)):
            result = self.ui_button.draw(self.screen)
            self.assertTrue(result)
        with patch('pygame.mouse.get_pos', return_value=(60, 60)), \
             patch('pygame.mouse.get_pressed', return_value=(0, 0, 0)):
            result = self.ui_button.draw(self.screen)
            self.assertFalse(result)
            self.assertFalse(self.ui_button.is_clicked)
            self.screen.blit.assert_called_with(self.ui_button.image, self.ui_button.rect)

    def test_draw_one_shot_release(self):
        # Test one-shot button after release
        with patch('pygame.mouse.get_pos', return_value=(60, 60)), \
             patch('pygame.mouse.get_pressed', return_value=(1, 0, 0)):
            result = self.ui_one_shot.draw(self.screen)
            self.assertTrue(result)
        with patch('pygame.mouse.get_pos', return_value=(60, 60)), \
             patch('pygame.mouse.get_pressed', return_value=(0, 0, 0)):
            result = self.ui_one_shot.draw(self.screen)
            self.assertFalse(result)
            self.assertFalse(self.ui_one_shot.is_clicked)  # Resets after release
            self.screen.blit.assert_called_with(self.ui_one_shot.image, self.ui_one_shot.rect)

    def test_draw_outside_click(self):
        # Test clicking outside button
        with patch('pygame.mouse.get_pos', return_value=(200, 200)), \
             patch('pygame.mouse.get_pressed', return_value=(1, 0, 0)):
            result = self.ui_button.draw(self.screen)
            self.assertFalse(result)
            self.assertFalse(self.ui_button.is_clicked)
            self.screen.blit.assert_called_with(self.ui_button.image, self.ui_button.rect)

if __name__ == '__main__':
    unittest.main()