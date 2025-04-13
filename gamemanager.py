# GameManager class for Alien Enigma
# Manages game state, nemesis spawning, and level progression

import pygame
import random
import settings as config
from nemesis import Nemesis
from nemesis_data import NEMESIS_SPAWN_DATA


class GameManager:
    def __init__(self, level_data, map_image):
        if not level_data or not map_image:
            raise ValueError("Level data and map image are required")

        self.level = 1
        self.game_speed = 1
        self.health = config.HEALTH
        self.money = config.MONEY
        self.tile_map = []
        self.waypoints = []
        self.level_data = level_data
        self.map_image = map_image
        self.nemesis_list = []
        self.spawned_nemesis = 0
        self.killed_nemesis = 0
        self.missed_nemesis = 0
        self.last_spawn = pygame.time.get_ticks()  # Initialize spawn timer
        self.nemesis_images = [pygame.Surface((32, 32))]  # Placeholder for nemesis sprites

    def process_data(self):
        # Extract tile map and waypoints from level data
        try:
            for layer in self.level_data["layers"]:
                if layer["name"] == "tilemap":
                    self.tile_map = layer["data"]
                elif layer["name"] == "waypoints":
                    for obj in layer["objects"]:
                        self.grab_waypoints(obj["polyline"])
        except KeyError as e:
            raise ValueError("Invalid level data format") from e

    def grab_waypoints(self, points):
        # Convert polyline data to (x, y) waypoints
        for point in points:
            x = point.get("x")
            y = point.get("y")
            if x is not None and y is not None:
                self.waypoints.append((x, y))

    def process_nemesis(self):
        # Queue nemesis spawns for the current level
        try:
            nemesis_data = NEMESIS_SPAWN_DATA[self.level - 1]
            for nemesis_type, count in nemesis_data.items():
                for _ in range(count):
                    self.nemesis_list.append(nemesis_type)
            random.shuffle(self.nemesis_list)  # Randomize spawn order
        except IndexError as e:
            raise ValueError("No nemesis data for level") from e

    def check_level_complete(self):
        # Check if all nemesis are handled
        total_handled = self.killed_nemesis + self.missed_nemesis
        return total_handled == len(self.nemesis_list)

    def reset_level(self):
        # Reset nemesis counters for a new level
        self.nemesis_list = []
        self.spawned_nemesis = 0
        self.killed_nemesis = 0
        self.missed_nemesis = 0

    def draw(self, screen):
        # Render map background
        screen.blit(self.map_image, (0, 0))

    def update(self, nemesis_group):
        # Spawn nemesis and update level state
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn > 2000 / self.game_speed and self.nemesis_list:
            nemesis_type = self.nemesis_list.pop(0)
            new_nemesis = Nemesis(nemesis_type, self.waypoints, self.nemesis_images)
            nemesis_group.add(new_nemesis)
            self.spawned_nemesis += 1
            self.last_spawn = current_time

        if self.check_level_complete():
            self.level += 1
            self.process_nemesis()