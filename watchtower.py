import pygame as pg
import math
import settings as c
from watchtower_data import WATCHTOWER_INFO

class WatchTower(pg.sprite.Sprite):
    def __init__(self, sprite_sheets, tile_x, tile_y, shot_fx):
        # Initialize a WatchTower sprite with sprite sheets, position, and sound
        try:
            pg.sprite.Sprite.__init__(self)
            self.upgrade_level = 4  # Initial upgrade level
            self.range = WATCHTOWER_INFO[self.upgrade_level - 1].get("range")  # Range from data
            self.cooldown = WATCHTOWER_INFO[self.upgrade_level - 1].get("cooldown")  # Cooldown from data
            self.last_shot = pg.time.get_ticks()  # Time of last shot
            self.selected = False  # Selection state
            self.target = None  # Current target enemy

            # Position variables
            self.tile_x = tile_x  # Tile X coordinate
            self.tile_y = tile_y  # Tile Y coordinate
            self.x = (self.tile_x + 0.5) * c.TILE_SIZE  # Center X in pixels
            self.y = (self.tile_y + 0.5) * c.TILE_SIZE  # Center Y in pixels
            self.shot_fx = shot_fx  # Shot sound effect

            # Animation variables
            self.sprite_sheets = sprite_sheets  # List of sprite sheets for upgrades
            self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])  # Animation frames
            self.frame_index = 0  # Current animation frame
            self.update_time = pg.time.get_ticks()  # Last animation update time

            # Update image
            self.angle = 90  # Initial rotation angle in degrees
            self.original_image = self.animation_list[self.frame_index]  # Current frame
            self.image = pg.transform.rotate(self.original_image, self.angle)  # Rotated image
            self.rect = self.image.get_rect()  # Rectangle for positioning
            self.rect.center = (self.x, self.y)  # Set initial position

            # Create transparent circle showing range
            self.range_image = pg.Surface((self.range * 2, self.range * 2))  # Range circle surface
            self.range_image.fill((0, 0, 0))  # Fill with black
            self.range_image.set_colorkey((0, 0, 0))  # Set black as transparent
            pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)  # Draw range circle
            self.range_image.set_alpha(100)  # Set transparency
            self.range_rect = self.range_image.get_rect()  # Range rectangle
            self.range_rect.center = self.rect.center  # Center range circle
        except IndexError as e:
            raise IndexError(f"Invalid upgrade_level or sprite_sheets index: {e}")
        except KeyError as e:
            raise ValueError(f"Missing key in Watch Tower Info for level {self.upgrade_level}: {e}")
        except TypeError as e:
            raise TypeError(f"Invalid parameters (sprite_sheets, tile_x, tile_y, shot_fx): {e}")
        except AttributeError as e:
            raise ValueError(f"Invalid sprite sheet or shot_fx: {e}")

    def load_images(self, sprite_sheet):
        # Extract images from a sprite sheet
        try:
            size = sprite_sheet.get_height()  # Frame size (assuming square)
            animation_list = []
            for x in range(c.ANIMATION_STEPS):
                temp_img = sprite_sheet.subsurface(x * size, 0, size, size)  # Extract frame
                animation_list.append(temp_img)
            return animation_list
        except AttributeError as e:
            print(f"Error loading images from sprite sheet: {e}")
            return []
        except pg.error as e:
            print(f"Pygame error in load_images: {e}")
            return []

    def update(self, enemy_group, world):
        # Update WatchTower state: target and animate
        try:
            if self.target:
                self.play_animation()  # Play firing animation if target exists
            else:
                # Search for new target after cooldown
                if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
                    self.pick_target(enemy_group)
        except AttributeError as e:
            print(f"Error in update: {e}")
        except ZeroDivisionError as e:
            print(f"Error with game_speed in update: {e}")

    def pick_target(self, enemy_group):
        # Find a target enemy within range
        try:
            for nemesis in enemy_group:
                if nemesis.health > 0:
                    x_dist = nemesis.pos[0] - self.x
                    y_dist = nemesis.pos[1] - self.y
                    dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
                    if dist < self.range:
                        self.target = nemesis
                        self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                        self.target.health -= c.DAMAGE
                        self.shot_fx.play()
                        break
        except AttributeError as e:
            print(f"Error picking target: {e}")
        except pg.error as e:
            print(f"Error playing shot sound: {e}")

    def play_animation(self):
        # Play firing animation
        try:
            self.original_image = self.animation_list[self.frame_index]  # Update frame
            if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
                self.update_time = pg.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.animation_list):
                    self.frame_index = 0  # Reset to idle
                    self.last_shot = pg.time.get_ticks()  # Record shot time
                    self.target = None  # Clear target
        except IndexError as e:
            print(f"Error in play_animation: Invalid frame_index {e}")
        except AttributeError as e:
            print(f"Error accessing animation_list: {e}")

    def upgrade(self):
        # Upgrade the WatchTower to the next level
        try:
            self.upgrade_level += 1
            self.range = WATCHTOWER_INFO[self.upgrade_level - 1].get("range")  # Update range
            self.cooldown = WATCHTOWER_INFO[self.upgrade_level - 1].get("cooldown")  # Update cooldown
            self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])  # Update animations
            self.original_image = self.animation_list[self.frame_index]  # Update image

            # Update range circle
            self.range_image = pg.Surface((self.range * 2, self.range * 2))
            self.range_image.fill((0, 0, 0))
            self.range_image.set_colorkey((0, 0, 0))
            pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
            self.range_image.set_alpha(100)
            self.range_rect = self.range_image.get_rect()
            self.range_rect.center = self.rect.center
        except IndexError as e:
            print(f"Error upgrading WatchTower: Invalid level index {e}")
        except KeyError as e:
            print(f"Missing key in WatchTower Info for level {self.upgrade_level}: {e}")
        except AttributeError as e:
            print(f"Error updating sprite sheet or range: {e}")

    def draw(self, surface):
        # Draw the WatchTower on the surface
        try:
            self.image = pg.transform.rotate(self.original_image, self.angle - 90)  # Rotate image
            self.rect = self.image.get_rect()
            self.rect.center = (self.x, self.y)
            surface.blit(self.image, self.rect)
            if self.selected:
                surface.blit(self.range_image, self.range_rect)  # Draw range circle if selected
        except TypeError as e:
            print(f"Error drawing WatchTower: Invalid surface {e}")
        except pg.error as e:
            print(f"Pygame error in draw: {e}")