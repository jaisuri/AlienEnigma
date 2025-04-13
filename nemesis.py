# Nemesis class for Alien Enigma
# Handles the bad guys that move along a path and get shot by the Watch Towers

import pygame
import math
from pygame.math import Vector2
import settings as config
from nemesis_data import NEMESIS_DATA

class Nemesis(pygame.sprite.Sprite):
    def __init__(self, nemesis_type, waypoints, images):
        # Set up a nemesis with its type, path, and picture
        pygame.sprite.Sprite.__init__(self)
        try:
            if not waypoints or not isinstance(waypoints, list):
                 print("Waypoints need to be a list with stuff in it!")
                 raise ValueError
            self.waypoints = waypoints           # Where the nemesis walks
            self.pos = Vector2(waypoints[0])     # Starting spot
            self.next_waypoint = 1               # Which point to head for next
            self.health = NEMESIS_DATA[nemesis_type]["health"]  # How tough it is
            self.speed = NEMESIS_DATA[nemesis_type]["speed"]    # How fast it moves
            self.angle = 0                       # For spinning the image
            self.base_image = images[nemesis_type]  # The unspun picture
            self.image = pygame.transform.rotate(self.base_image, self.angle)  # Spun picture
            self.rect = self.image.get_rect(center=self.pos)  # Where to draw it
            # Point at next waypoint to start
            self.target = Vector2(waypoints[1] if len(waypoints) > 1 else waypoints[0])
        except:
            print(f"Unable to initialise nemesis module.")


    def update(self, game_world):
        # Move, spin, and check if this nemesis is still kicking
        self.move(game_world)
        self.rotate()
        self.check_alive(game_world)

    def move(self, game_world):
        # Head toward the next waypoint or finish the path
        if self.next_waypoint < len(self.waypoints):
            target = Vector2(self.waypoints[self.next_waypoint])
            direction = target - self.pos
            distance = direction.length()
            move_speed = self.speed * game_world.game_speed
            if distance >= move_speed:
                self.pos += direction.normalize() * move_speed
            else:
                # Close enough, snap to it
                if distance:
                    self.pos += direction.normalize() * distance
                self.next_waypoint += 1
            self.target = target  # Update target for rotation
        else:
            # Reached the end - oops!
            self.kill()
            game_world.health -= 1
            game_world.missed_nemesis += 1
        self.rect.center = self.pos
        
    def rotate(self):
        # Turn to face the next waypoint
        if self.target is None:
            print("No target to rotate toward - skipping!")
            return
        direction = self.target - self.pos
        self.angle = math.degrees(math.atan2(-direction[1], direction[0]))
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def check_alive(self, game_world):
        # See if the nemesis got defeated
        if self.health <= 0:
            game_world.killed_nemesis += 1
            game_world.money += config.KILL_REWARD
            self.kill()
