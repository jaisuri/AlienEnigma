# main_menu.py
import pygame as pg
import sys
import math
import os
import random

class Menu:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Colors
        self.bg_color = (20, 20, 40)
        self.button_color = (60, 80, 120)
        self.hover_color = (100, 120, 180)
        self.text_color = (220, 240, 255)
        self.accent_color = (255, 50, 100)
        
        # Fonts with fallback
        self.title_font = None
        self.button_font = None
        try:
            if os.path.exists("assets/fonts/SpaceFont.ttf"):
                self.title_font = pg.font.Font("assets/fonts/SpaceFont.ttf", 72)
                self.button_font = pg.font.Font("assets/fonts/SpaceFont.ttf", 28)
            else:
                raise FileNotFoundError("Custom font not found")
        except Exception as e:
            print(f"Failed to load custom font: {e}. Using fallback.")
            self.title_font = pg.font.SysFont("Arial", 72, bold=True)
            self.button_font = pg.font.SysFont("Arial", 28, bold=True)
        
        # Load assets with error handling
        self.background = None
        self.logo = None
        try:
            if os.path.exists("assets/images/backgrounds/menu_bg.png"):
                self.background = pg.image.load("assets/images/backgrounds/menu_bg.png").convert()
                self.background = pg.transform.scale(self.background, (screen_width, screen_height))
            else:
                raise FileNotFoundError("Background image not found")
        except Exception as e:
            print(f"Failed to load background image: {e}. Using solid color.")
        
        try:
            if os.path.exists("assets/images/ui/logo.png"):
                self.logo = pg.image.load("assets/images/ui/logo.png").convert_alpha()
                self.logo = pg.transform.scale(self.logo, (300, 100))
            else:
                raise FileNotFoundError("Logo image not found")
        except Exception as e:
            print(f"Failed to load logo image: {e}. Skipping logo.")
        
        # Audio with detailed error handling
        self.volume = 0.5
        self.music_on = False
        self.click_sound = None
        
        try:
            pg.mixer.init(frequency=44100, size=-16, channels=2)
            music_path = "assets/audio/menu_music.mp3"
            click_path = "assets/audio/click.mp3"
            
            # Load menu music
            if os.path.exists(music_path):
                try:
                    pg.mixer.music.load(music_path)
                    pg.mixer.music.set_volume(self.volume)
                    pg.mixer.music.play(-1)
                    self.music_on = True
                    print(f"Successfully loaded menu music: {music_path}")
                except pg.error as e:
                    print(f"Failed to load {music_path}: {e}. Likely an unsupported WAV format.")
            else:
                print(f"Menu music file not found: {music_path}")
            
            # Load click sound
            if os.path.exists(click_path):
                try:
                    self.click_sound = pg.mixer.Sound(click_path)
                    print(f"Successfully loaded click sound: {click_path}")
                except pg.error as e:
                    print(f"Failed to load {click_path}: {e}. Likely an unsupported WAV format.")
            else:
                print(f"Click sound file not found: {click_path}")
        except Exception as e:
            print(f"Mixer initialization failed: {e}. Proceeding without sound.")
            self.music_on = False
        
        # Button properties
        self.button_width = 300
        self.button_height = 60
        self.button_spacing = 25
        self.center_x = screen_width // 2 - self.button_width // 2
        self.start_y = screen_height // 2 - 50
        
        # Buttons
        self.buttons = [
            {"text": "Start Game", "rect": pg.Rect(self.center_x, self.start_y, self.button_width, self.button_height), "action": "start", "hover": False, "scale": 1.0},
            {"text": "How to Play", "rect": pg.Rect(self.center_x, self.start_y + (self.button_height + self.button_spacing), self.button_width, self.button_height), "action": "how_to", "hover": False, "scale": 1.0},
            {"text": f"Volume: {int(self.volume * 100)}", "rect": pg.Rect(self.center_x, self.start_y + 2 * (self.button_height + self.button_spacing), self.button_width, self.button_height), "action": "volume", "hover": False, "scale": 1.0},
            {"text": "Music: On" if self.music_on else "Music: Off", "rect": pg.Rect(self.center_x, self.start_y + 3 * (self.button_height + self.button_spacing), self.button_width, self.button_height), "action": "music", "hover": False, "scale": 1.0},
            {"text": "Exit", "rect": pg.Rect(self.center_x, self.start_y + 4 * (self.button_height + self.button_spacing), self.button_width, self.button_height), "action": "exit", "hover": False, "scale": 1.0}
        ]
        
        # Animation variables
        self.time = 0
        self.particles = []
        
        # How to Play screen
        self.show_how_to = False
        self.how_to_text = [
            "Welcome to Alien Enigma!",
            "1. Place watchtowers to defend against enemies",
            "2. Upgrade towers to increase their power",
            "3. Survive all waves to win",
            "4. Click Start Game to begin",
            "Click anywhere to return to menu"
        ]

    def create_particle(self):
        """Create a particle for background star effect."""
        x = random.randint(0, self.screen_width)
        y = 0
        speed = random.uniform(1, 3)
        size = random.randint(1, 3)
        return {"x": x, "y": y, "speed": speed, "size": size}

    def update_particles(self):
        """Update particle positions for animation."""
        self.time += 0.1
        if random.random() < 0.1:
            self.particles.append(self.create_particle())
        
        for particle in self.particles[:]:
            particle["y"] += particle["speed"]
            if particle["y"] > self.screen_height:
                self.particles.remove(particle)

    def draw_text(self, text, font, color, x, y, center=False):
        """Render text on the screen."""
        try:
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(x, y)) if center else text_surface.get_rect(topleft=(x, y))
            self.screen.blit(text_surface, text_rect)
        except Exception as e:
            print(f"Error rendering text: {e}")

    def draw_button(self, button):
        """Draw a button with hover animation and neon border."""
        target_scale = 1.05 if button["hover"] else 1.0
        button["scale"] += (target_scale - button["scale"]) * 0.2
        
        width = int(self.button_width * button["scale"])
        height = int(self.button_height * button["scale"])
        button_surface = pg.Surface((width, height), pg.SRCALPHA)
        
        color = self.hover_color if button["hover"] else self.button_color
        pg.draw.rect(button_surface, color, (0, 0, width, height), border_radius=15)
        pg.draw.rect(button_surface, self.accent_color, (0, 0, width, height), 2, border_radius=15)
        
        text_surface = self.button_font.render(button["text"], True, self.text_color)
        text_rect = text_surface.get_rect(center=(width // 2, height // 2))
        button_surface.blit(text_surface, text_rect)
        
        x = button["rect"].x - (width - self.button_width) // 2
        y = button["rect"].y - (height - self.button_height) // 2
        self.screen.blit(button_surface, (x, y))

    def draw(self):
        """Draw the entire menu screen."""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.bg_color)
        
        for particle in self.particles:
            pg.draw.circle(self.screen, self.text_color, 
                        (int(particle["x"]), int(particle["y"])), 
                        particle["size"])
        
        if not self.show_how_to:  # Only draw title/logo when not showing how-to
            if self.logo:
                scale = 1.0 + math.sin(self.time) * 0.05
                scaled_logo = pg.transform.scale(self.logo, 
                                            (int(300 * scale), int(100 * scale)))
                logo_rect = scaled_logo.get_rect(center=(self.screen_width // 2, 150))
                self.screen.blit(scaled_logo, logo_rect)
            else:
                self.draw_text("Alien Enigma", self.title_font, self.text_color, 
                            self.screen_width // 2, 150, center=True)
        
        if self.show_how_to:
            pg.draw.rect(self.screen, (0, 0, 0, 180), (0, 0, self.screen_width, self.screen_height))
            y = 200
            for line in self.how_to_text:
                self.draw_text(line, self.button_font, self.text_color, 
                            self.screen_width // 2, y, center=True)
                y += 40
        else:
            for button in self.buttons:
                self.draw_button(button)

    def handle_events(self):
        """Handle user input and return actions."""
        mouse_pos = pg.mouse.get_pos()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "exit"
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.show_how_to:
                    self.show_how_to = False
                    if self.click_sound:
                        self.click_sound.play()
                    return None
                
                for button in self.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        if self.click_sound:
                            self.click_sound.play()
                        if button["action"] == "volume":
                            self.volume = min(1.0, max(0.0, self.volume + 0.1 if self.volume < 1.0 else -0.9))
                            if self.music_on:
                                pg.mixer.music.set_volume(self.volume)
                            button["text"] = f"Volume: {int(self.volume * 100)}"
                        elif button["action"] == "music":
                            self.music_on = not self.music_on
                            if self.music_on and pg.mixer.get_init():
                                pg.mixer.music.play(-1)
                            elif pg.mixer.get_init():
                                pg.mixer.music.stop()
                            button["text"] = "Music: On" if self.music_on else "Music: Off"
                        elif button["action"] == "how_to":
                            self.show_how_to = True
                        else:
                            return button["action"]
        
        for button in self.buttons:
            button["hover"] = button["rect"].collidepoint(mouse_pos)
        
        return None

    def run(self):
        """Main loop for the menu."""
        self.update_particles()
        self.draw()
        return self.handle_events()

if __name__ == "__main__":
    pg.init()
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 600
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Alien Enigma - Main Menu")
    clock = pg.time.Clock()
    
    menu = Menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    running = True
    
    while running:
        action = menu.run()
        if action == "start":
            print("Starting game...")
        elif action == "exit":
            running = False
        
        pg.display.flip()
        clock.tick(60)
    
    pg.quit()
    sys.exit()