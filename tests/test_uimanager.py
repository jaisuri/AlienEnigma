import unittest
import pygame as pg
from unittest.mock import Mock, patch
from uimanager import UIManager  # Assuming your code is in button.py

class TestUIManager(unittest.TestCase):
    def setUp(self):
        # Initialize pygame for tests
        pg.init()
        # Create a test surface and image
        self.test_surface = pg.Surface((800, 600))
        self.test_image = pg.Surface((100, 50))
        # Create a basic button instance
        self.uimanager = UIManager(100, 100, self.test_image, False)

    def tearDown(self):
        pg.quit()

    def test_init_valid_parameters(self):
        #Test button initialization with valid parameters
        uimanager = UIManager(50, 50, self.test_image, True)
        self.assertEqual(uimanager.rect.topleft, (50, 50))
        self.assertFalse(uimanager.clicked)
        self.assertTrue(uimanager.single_click)
        self.assertEqual(uimanager.image, self.test_image)

    def test_init_invalid_image(self):
        #Test initialization with invalid image
        with self.assertRaises(ValueError):
            UIManager(0, 0, None, False)

    def test_init_invalid_coordinates(self):
        #Test initialization with invalid coordinate types
        with self.assertRaises(TypeError):
            UIManager("invalid", 0, self.test_image, False)

    @patch('pygame.mouse.get_pos')
    @patch('pygame.mouse.get_pressed')
    def test_draw_no_click(self, mock_get_pressed, mock_get_pos):
        #Test draw method when button is not clicked
        mock_get_pos.return_value = (0, 0)  # Mouse outside button
        mock_get_pressed.return_value = (0, 0, 0)  # No buttons pressed
        
        action = self.uimanager.draw(self.test_surface)
        self.assertFalse(action)
        self.assertFalse(self.uimanager.clicked)

    @patch('pygame.mouse.get_pos')
    @patch('pygame.mouse.get_pressed')
    def test_draw_single_click(self, mock_get_pressed, mock_get_pos):
        #Test draw method with single-click button
        uimanager = UIManager(0, 0, self.test_image, True)
        mock_get_pos.return_value = (10, 10)  # Mouse over button
        mock_get_pressed.return_value = (1, 0, 0)  # Left mouse button pressed
        
        # First click
        action = uimanager.draw(self.test_surface)
        self.assertTrue(action)
        self.assertTrue(uimanager.clicked)

        # Second click while still pressed
        action = uimanager.draw(self.test_surface)
        self.assertFalse(action)  # No action on second call while clicked

    @patch('pygame.mouse.get_pos')
    @patch('pygame.mouse.get_pressed')
    def test_draw_multi_click(self, mock_get_pressed, mock_get_pos):
        #Test draw method with multi-click button
        uimanager = UIManager(0, 0, self.test_image, False)
        mock_get_pos.return_value = (10, 10)  # Mouse over button
        mock_get_pressed.return_value = (1, 0, 0)  # Left mouse uimanager pressed
        
        # Multiple clicks should all trigger action
        for _ in range(3):
            action = uimanager.draw(self.test_surface)
            self.assertTrue(action)
            self.assertFalse(uimanager.clicked)  # Reset each time

    @patch('pygame.mouse.get_pos')
    def test_draw_reset_clicked(self, mock_get_pos):
        #Test clicked state resets when mouse released
        self.uimanager.clicked = True
        mock_get_pos.return_value = (10, 10)
        
        with patch('pygame.mouse.get_pressed', return_value=(0, 0, 0)):
            self.uimanager.draw(self.test_surface)
            self.assertFalse(self.uimanager.clicked)

if __name__ == '__main__':
    unittest.main()