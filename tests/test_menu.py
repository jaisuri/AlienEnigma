import unittest
from unittest.mock import Mock, patch
import pygame as pg
import sys
sys.path.append("..")
from menu import Menu

class TestMenu(unittest.TestCase):
    def setUp(self):
        pg.init()
        self.screen = Mock(spec=pg.Surface)
        self.menu = Menu(self.screen, 1200, 600)
        self.menu.title_font = Mock()
        self.menu.button_font = Mock()
        self.menu.click_sound = Mock()
        self.menu.background = None
        self.menu.logo = None
        self.menu.center_x = 450
        self.menu.start_y = 250
        self.menu.buttons = [
            {"text": "Start Game", "rect": pg.Rect(450, 250, 300, 60), "action": "start", "hover": False, "scale": 1.0},
            {"text": "How to Play", "rect": pg.Rect(450, 335, 300, 60), "action": "how_to", "hover": False, "scale": 1.0},
            {"text": f"Volume: {int(self.menu.volume * 100)}%", "rect": pg.Rect(450, 420, 300, 60), "action": "volume", "hover": False, "scale": 1.0},
            {"text": "Music: On" if self.menu.music_on else "Music: Off", "rect": pg.Rect(450, 505, 300, 60), "action": "music", "hover": False, "scale": 1.0},
            {"text": "Exit", "rect": pg.Rect(450, 590, 300, 60), "action": "exit", "hover": False, "scale": 1.0}
        ]

    def tearDown(self):
        pg.quit()

    def test_init(self):
        self.assertEqual(self.menu.screen_width, 1200)
        self.assertEqual(self.menu.screen_height, 600)
        self.assertEqual(self.menu.volume, 0.5)
        self.assertEqual(len(self.menu.buttons), 5)
        self.assertEqual(self.menu.buttons[2]["text"], "Volume: 50%")
        self.assertFalse(self.menu.show_how_to)

    def test_create_particle(self):
        particle = self.menu.create_particle()
        self.assertTrue(0 <= particle["x"] <= 1200)
        self.assertEqual(particle["y"], 0)
        self.assertTrue(1 <= particle["speed"] <= 3)
        self.assertTrue(1 <= particle["size"] <= 3)

    def test_update_particles(self):
        # Test particle creation
        with patch('random.random', return_value=0.05):
            self.menu.update_particles()
            self.assertGreaterEqual(len(self.menu.particles), 1)
        
        # Test particle movement
        particle = {"x": 100, "y": 0, "speed": 2, "size": 2}
        self.menu.particles = [particle]
        self.menu.update_particles()
        self.assertGreater(particle["y"], 0)
        
        # Test particle removal
        self.menu.particles = [{"x": 100, "y": 601, "speed": 2, "size": 2}]  # Fresh particle
        self.menu.update_particles()
        self.assertEqual(len(self.menu.particles), 0)

    def test_draw_text(self):
        self.menu.button_font.render.return_value = Mock()
        self.menu.draw_text("Test", self.menu.button_font, (255, 255, 255), 100, 100)
        self.menu.button_font.render.assert_called_with("Test", True, (255, 255, 255))
        self.screen.blit.assert_called()

    def test_draw_button(self):
        button = self.menu.buttons[0]
        button["hover"] = True
        with patch('pygame.draw.rect'), patch('pygame.Surface') as mock_surface:
            mock_surface.return_value = Mock()
            self.menu.button_font.render.return_value = Mock()
            self.menu.draw_button(button)
            self.assertGreater(button["scale"], 1.0)

    @patch('pygame.mouse.get_pos', return_value=(600, 420))
    @patch('pygame.event.get', return_value=[Mock(type=pg.MOUSEBUTTONDOWN, button=1)])
    def test_handle_events_volume(self, mock_event, mock_mouse):
        with patch('pygame.mixer.music.set_volume') as mock_set_volume:
            action = self.menu.handle_events()
            self.assertIsNone(action)
            self.assertAlmostEqual(self.menu.volume, 0.6, places=1)
            self.assertEqual(self.menu.buttons[2]["text"], "Volume: 60%")
            mock_set_volume.assert_called_with(0.6)
            self.menu.click_sound.play.assert_called_once()

    @patch('pygame.mouse.get_pos', return_value=(600, 505))
    @patch('pygame.event.get', return_value=[Mock(type=pg.MOUSEBUTTONDOWN, button=1)])
    def test_handle_events_music(self, mock_event, mock_mouse):
        self.menu.music_on = True
        with patch('pygame.mixer.music.stop') as mock_stop, patch('pygame.mixer.music.play') as mock_play:
            action = self.menu.handle_events()
            self.assertIsNone(action)
            self.assertFalse(self.menu.music_on)
            self.assertEqual(self.menu.buttons[3]["text"], "Music: Off")
            mock_stop.assert_called_once()
            mock_play.assert_not_called()

    @patch('pygame.mouse.get_pos', return_value=(600, 590))
    @patch('pygame.event.get', return_value=[Mock(type=pg.MOUSEBUTTONDOWN, button=1)])
    def test_handle_events_exit(self, mock_event, mock_mouse):
        action = self.menu.handle_events()
        self.assertEqual(action, "exit")
        self.menu.click_sound.play.assert_called_once()

    @patch('pygame.mouse.get_pos', return_value=(600, 335))
    @patch('pygame.event.get', return_value=[Mock(type=pg.MOUSEBUTTONDOWN, button=1)])
    def test_handle_events_how_to(self, mock_event, mock_mouse):
        action = self.menu.handle_events()
        self.assertIsNone(action)
        self.assertTrue(self.menu.show_how_to)

    def test_draw_how_to(self):
        self.menu.show_how_to = True
        with patch('pygame.draw.rect'), patch.object(self.menu, 'draw_text') as mock_draw_text:
            self.menu.draw()
            self.assertEqual(mock_draw_text.call_count, len(self.menu.how_to_text))

if __name__ == '__main__':
    unittest.main()