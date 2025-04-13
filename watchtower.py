# WatchTower class for Alien Enigma
# Shoots at nemesis to protect the base, with cool animations

import pygame
import math
import settings as config
from watchtower_data import WATCHTOWER_INFO

class WatchTower(pygame.sprite.Sprite):
    def __init__(self, sprite_sheets, tile_x, tile_y, shot_sound):
        # Set up a watchtower at a tile position with sprites and sound
        pygame.sprite.Sprite.__init__(self)
        try:
            self.level = 1                  # Starting upgrade level
            self.range = WATCHTOWER_INFO[self.level - 1]["range"]  # How far it shoots
            self.cooldown = WATCHTOWER_INFO[self.level - 1]["cooldown"]  # Time between shots
            self.last_shot = pygame.time.get_ticks()  # When it last fired
            self.selected = False           # If player clicked it
            self.target = None              # Which nemesis to aim at

            # Position on the grid and in pixels
            self.tile_x = tile_x
            self.tile_y = tile_y
            self.x = (tile_x + 0.5) * config.TILE_SIZE
            self.y = (tile_y + 0.5) * config.TILE_SIZE
            self.shot_sound = shot_sound    # Pew pew sound

            # Animation stuff
            self.sprite_sheets = sprite_sheets
            self.frames = self._load_frames(sprite_sheets[self.level - 1])
            self.frame_index = 0            # Which frame we're showing
            self.frame_time = pygame.time.get_ticks()  # Last frame switch

            # Image and rotation
            self.angle = 90                 # Starts facing up
            self.base_image = self.frames[self.frame_index]
            self.image = pygame.transform.rotate(self.base_image, self.angle)
            self.rect = self.image.get_rect(center=(self.x, self.y))

            # Range circle for when selected
            self._make_range_circle()
        except:
            print("Error initialising Watch Tower module.")


    def _load_frames(self, sheet):
        # Cut up the sprite sheet into animation frames
        try:
            size = sheet.get_height()
            frame_list = []
            for x in range(config.ANIMATION_STEPS):
                frame = sheet.subsurface(x * size, 0, size, size)
                frame_list.append(frame)
            return frame_list
        except pygame.error:
            print("Pygame didn't like that sprite sheet!")
            return []

    def _make_range_circle(self):
        # Create a see-through circle to show shooting range
        try:
            self.range_image = pygame.Surface((self.range * 2, self.range * 2))
            self.range_image.fill((0, 0, 0))
            self.range_image.set_colorkey((0, 0, 0))
            pygame.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
            self.range_image.set_alpha(100)
            self.range_rect = self.range_image.get_rect(center=self.rect.center)
        except pygame.error:
            print("Couldn't make the range circle. Weird!")

    def update(self, nemesis_group, game_world):
        # Check for targets and animate if shooting
        try:
            if self.target:
                self.animate()
            elif pygame.time.get_ticks() - self.last_shot > (self.cooldown / game_world.game_speed):
                self.find_nemesis(nemesis_group)
        except AttributeError:
            print("Something's went wrong in watchtower update!")

    def find_nemesis(self, nemesis_group):
        # Pick a nemesis to shoot at if in range
        try:
            for nemesis in nemesis_group:
                if nemesis.health > 0:
                    distance = math.hypot(nemesis.pos[0] - self.x, nemesis.pos[1] - self.y)
                    if distance < self.range:
                        self.target = nemesis
                        self.angle = math.degrees(math.atan2(-(nemesis.pos[1] - self.y), nemesis.pos[0] - self.x))
                        nemesis.health -= config.DAMAGE
                        self.shot_sound.play()
                        break
        except AttributeError:
            print("Can't aim at the nemesis or world data is corrupt.")

    def animate(self):
        # Play shooting animation
        try:
            self.base_image = self.frames[self.frame_index]
            if pygame.time.get_ticks() - self.frame_time > config.ANIMATION_DELAY:
                self.frame_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.frames):
                    self.frame_index = 0
                    self.last_shot = pygame.time.get_ticks()
                    self.target = None
        except IndexError:
            print("Animation frame went out of bounds!")

    def upgrade(self):
        # Level up the watchtower
        try:
            self.level += 1
            self.range = WATCHTOWER_INFO[self.level - 1]["range"]
            self.cooldown = WATCHTOWER_INFO[self.level - 1]["cooldown"]
            self.frames = self._load_frames(self.sprite_sheets[self.level - 1])
            self.base_image = self.frames[self.frame_index]
            self._make_range_circle()
        except IndexError:
            print("Can't upgrade - no more levels!")

    def draw(self, screen):
        # Show the watchtower and its range if selected
        try:
            self.image = pygame.transform.rotate(self.base_image, self.angle - 90)
            self.rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, self.rect)
            if self.selected:
                screen.blit(self.range_image, self.range_rect)
        except pygame.error:
            print("Trouble drawing the watchtower!")