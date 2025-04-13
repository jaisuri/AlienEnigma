# GameManager class for Alien Enigma
# Manages the game world, nemesis spawning, and level progression

import pygame
import random
import settings as config
from nemesis_data import NEMESIS_SPAWN_DATA

class GameManager:
    def __init__(self, level_data, map_image):
        # Set up the game world with level data and background map
        try:
            self.level = 1                  # Starting level
            self.game_speed = 1             # Controls how fast things move
            self.health = config.HEALTH     # Player's health points
            self.money = config.MONEY       # Starting cash for buying watchtowers
            self.tile_map = []              # Holds the map's tile layout
            self.waypoints = []             # Path coordinates for nemesis
            self.level_data = level_data    # Raw JSON from level file
            self.map_image = map_image      # Background image for the map
            self.nemesis_list = []          # Types of nemesis to spawn
            self.spawned_nemesis = 0        # How many nemesis have spawned
            self.killed_nemesis = 0         # Nemesis defeated
            self.missed_nemesis = 0         # Nemesis that got away
        except:
            print("Error initialising the Game manager module.")


    def process_data(self):
        # Pull tile map and waypoints from the JSON data
        try:
            for layer in self.level_data["layers"]:
                if layer["name"] == "tilemap":
                    self.tile_map = layer["data"]  # Grab the tile layout
                elif layer["name"] == "waypoints":
                    for obj in layer["objects"]:
                        points = obj["polyline"]
                        self.grab_waypoints(points)  # Extract path coordinates
        except:
            print(f"Error in level data.")

    def grab_waypoints(self, points):
        # Turn polyline data into usable (x, y) waypoints
        for point in points:
            x = point.get("x")
            y = point.get("y")
            if x is not None and y is not None:
                self.waypoints.append((x, y))  # Add to path
            else:
                print(f"Bad waypoint data: {point}")

    def process_nemesis(self):
        # Set up nemesis spawn order for the level
        nemesis_data = NEMESIS_SPAWN_DATA[self.level - 1]  # Get this level's nemesis
        for nemesis_type, count in nemesis_data.items():
            for _ in range(count):
                self.nemesis_list.append(nemesis_type)  # Queue up nemesis
        random.shuffle(self.nemesis_list)  # Randomising the nemesis

    def check_level_complete(self):
        # See if we've killed all nemesis
        total_handled = self.killed_nemesis + self.missed_nemesis
        if total_handled == len(self.nemesis_list):
            return True
        return False

    def reset_level(self):
        # Clear out nemesis data for a fresh level
        self.nemesis_list = []         # Empty the spawn list
        self.spawned_nemesis = 0       # Reset spawn counter
        self.killed_nemesis = 0        # Reset kills
        self.missed_nemesis = 0        # Reset escapes

    def draw(self, screen):
        # Draw the map background
        screen.blit(self.map_image, (0, 0))  # Place map at top-left
    
    def update(self, nemesis_group):
    # Update game state, like spawning nemesis
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn > 2000 / self.game_speed:
            if self.nemesis_list:
                nemesis_type = self.nemesis_list.pop(0)
                new_nemesis = Nemesis(nemesis_type, self.waypoints)
                nemesis_group.add(new_nemesis)
                self.spawned_nemesis += 1
                self.last_spawn = current_time

        # Check level completion
        if self.check_level_complete():
            self.level += 1
            self.process_nemesis()