import pygame as pg
from pygame.math import Vector2
import math
import settings as c
from nemesis_data import NEMESIS_DATA

class Nemesis(pg.sprite.Sprite):
    def __init__(self, enemy_type, waypoints, images):
        # Initialize a Nemesis sprite with type, waypoints, and image
        try:
            pg.sprite.Sprite.__init__(self)
            if not waypoints or not isinstance(waypoints, list):
                raise ValueError("Waypoints must be a non-empty list")
            self.waypoints = waypoints  # List of waypoints for movement
            self.pos = Vector2(self.waypoints[0])  # Starting position
            self.target_waypoint = 1  # Index of next waypoint
            self.health = NEMESIS_DATA.get(enemy_type)["health"]  # Health from data
            self.speed = NEMESIS_DATA.get(enemy_type)["speed"]  # Speed from data
            self.angle = 0  # Initial rotation angle in degrees
            self.original_image = images.get(enemy_type)  # Original sprite image
            self.image = pg.transform.rotate(self.original_image, self.angle)  # Rotated image
            self.rect = self.image.get_rect()  # Rectangle for positioning
            self.rect.center = self.pos  # Set initial position
        except KeyError as e:
            raise ValueError(f"Invalid enemy_type '{enemy_type}' in NEMESIS_DATA: {e}")
        except IndexError as e:
            raise IndexError(f"Invalid waypoints list: {e}")
        except TypeError as e:
            raise TypeError(f"Invalid parameters (enemy_type, waypoints, or images): {e}")
        except AttributeError as e:
            raise ValueError(f"Invalid image for enemy_type '{enemy_type}': {e}")

    def update(self, world):
        # Update Nemesis state: move, rotate, and check if alive
        try:
            self.move(world)  # Move along waypoints
            self.rotate()  # Rotate towards next waypoint
            self.check_alive(world)  # Check health and update world stats
        except Exception as e:
            print(f"Error in update: {e}")

    def move(self, world):
        # Move Nemesis towards the next waypoint
        try:
            if self.target_waypoint < len(self.waypoints):
                self.target = Vector2(self.waypoints[self.target_waypoint])  # Next waypoint
                self.movement = self.target - self.pos  # Movement vector
            else:
                # Nemesis reached the end of the path
                self.kill()
                world.health -= 1
                world.missed_enemies += 1
                return

            # Calculate distance to target
            dist = self.movement.length()
            # Adjust position based on speed and game speed
            if dist >= (self.speed * world.game_speed):
                self.pos += self.movement.normalize() * (self.speed * world.game_speed)
            else:
                if dist != 0:
                    self.pos += self.movement.normalize() * dist
                self.target_waypoint += 1
        except IndexError as e:
            print(f"IndexError in move: {e}, target_waypoint={self.target_waypoint}")
        except AttributeError as e:
            print(f"Error accessing world.game_speed: {e}")
        except ValueError as e:
            print(f"Error normalizing movement vector: {e}")

    def rotate(self):
        # Rotate Nemesis to face the next waypoint
        try:
            # Calculate distance to next waypoint
            dist = self.target - self.pos
            # Calculate angle in degrees
            self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
            # Rotate image and update rectangle
            self.image = pg.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
        except AttributeError as e:
            print(f"Error rotating Nemesis: {e}")
        except ValueError as e:
            print(f"Error calculating angle: {e}")

    def check_alive(self, world):
        # Check if Nemesis is still alive and update world stats
        try:
            if self.health <= 0:
                world.killed_enemies += 1
                world.money += c.KILL_REWARD
                self.kill()
        except AttributeError as e:
            print(f"Error checking alive status: {e}")