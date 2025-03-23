import pygame as pg
import random
import settings as c
from nemesis_data import NEMESIS_SPAWN_DATA

class GameManager():
    def __init__(self, data, map_image):
        # Initialize the GameManager with level data and map image
        try:
            self.level = 1  # Current level
            self.game_speed = 1  # Game speed multiplier
            self.health = c.HEALTH  # Player health
            self.money = c.MONEY  # Player money
            self.tile_map = []  # Tile map data
            self.waypoints = []  # List of waypoints for enemies
            self.level_data = data  # Raw level data from JSON
            self.image = map_image  # Map image (Pygame Surface)
            self.enemy_list = []  # List of enemy types to spawn
            self.spawned_enemies = 0  # Number of spawned enemies
            self.killed_enemies = 0  # Number of killed enemies
            self.missed_enemies = 0  # Number of missed enemies
        except AttributeError as e:
            raise ValueError(f"Invalid map_image: {e}")
        except TypeError as e:
            raise TypeError(f"Invalid data parameter: {e}")

    def process_data(self):
        # Process level data to extract tile map and waypoints
        try:
            for layer in self.level_data["layers"]:
                if layer["name"] == "tilemap":
                    self.tile_map = layer["data"]  # Extract tile map
                elif layer["name"] == "waypoints":
                    for obj in layer["objects"]:
                        waypoint_data = obj["polyline"]
                        self.process_waypoints(waypoint_data)  # Extract waypoints
        except KeyError as e:
            print(f"Error processing level data: Missing key {e}")
        except TypeError as e:
            print(f"Error in level data structure: {e}")

    def process_waypoints(self, data):
        # Extract individual waypoint coordinates from polyline data
        try:
            for point in data:
                temp_x = point.get("x")
                temp_y = point.get("y")
                if temp_x is not None and temp_y is not None:
                    self.waypoints.append((temp_x, temp_y))
                else:
                    print(f"Warning: Invalid waypoint in polyline data: {point}")
        except TypeError as e:
            print(f"Error processing waypoints: Invalid data {e}")

    def process_enemies(self):
        # Generate and shuffle enemy list for the current level
        try:
            enemies = NEMESIS_SPAWN_DATA[self.level - 1]  # Enemy data for current level
            for enemy_type in enemies:
                enemies_to_spawn = enemies[enemy_type]
                for _ in range(enemies_to_spawn):
                    self.enemy_list.append(enemy_type)
            random.shuffle(self.enemy_list)  # Randomize enemy order
        except IndexError as e:
            print(f"Error processing enemies: Invalid level index {e}")
        except KeyError as e:
            print(f"Error in NEMESIS_SPAWN_DATA: Missing enemy type {e}")
        except TypeError as e:
            print(f"Error in enemy data structure: {e}")

    def check_level_complete(self):
        # Check if the level is complete (all enemies processed)
        try:
            if (self.killed_enemies + self.missed_enemies) == len(self.enemy_list):
                return True
            return False
        except AttributeError as e:
            print(f"Error checking level completion: {e}")
            return False

    def reset_level(self):
        # Reset enemy-related variables for a new level
        try:
            self.enemy_list = []  # Clear enemy list
            self.spawned_enemies = 0  # Reset spawned count
            self.killed_enemies = 0  # Reset killed count
            self.missed_enemies = 0  # Reset missed count
        except AttributeError as e:
            print(f"Error resetting level: {e}")

    def draw(self, surface):
        # Draw the map image on the given surface
        try:
            surface.blit(self.image, (0, 0))
        except TypeError as e:
            print(f"Error drawing world: Invalid surface or image {e}")
        except pg.error as e:
            print(f"Pygame error drawing world: {e}")