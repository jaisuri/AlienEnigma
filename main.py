# Main class for Alien Enigma
# Initialises and controls the game world, nemesis andwatch towers 

import pygame as pg
import json
from nemesis import Nemesis
from gamemanager import GameManager
from watchtower import WatchTower
from uimanager import UIManager
import settings as c
from menu import Menu

# Initialize Pygame
try:
    pg.init()
except Exception as e:
    print(f"Failed to initialize Pygame: {e}")
    pg.quit()

# Setup clock for controlling frame rate
clock = pg.time.Clock()

# Create game window
try:
    screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.display.set_caption("Alien Enigma")
except:
    print(f"Error in initialising the screen")
    pg.quit()

# Initialize MainMenu
menu = Menu(screen, c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT)
game_state = "menu"

# Game state variables
game_over = False
game_outcome = 0
level_started = False
last_nemesis_spawn = pg.time.get_ticks()
placing_watchtower = False
selected_watchtower = None

# Load game assets
try:
    map_image = pg.image.load('assets/images/levels/level.png').convert_alpha()
    watchtower_spritesheets = [
        pg.image.load(f'assets/images/watchtowers/watchtower_{x}.png').convert_alpha()
        for x in range(1, c.WATCHTOWER_LEVELS + 1)
    ]
    cursor_watchtower = pg.image.load('assets/images/watchtowers/cursor_watchtower.png').convert_alpha()
    nemesis_images = {
        "weak": pg.image.load('assets/images/nemesis/nemesis_1.png').convert_alpha(),
        "medium": pg.image.load('assets/images/nemesis/nemesis_2.png').convert_alpha(),
        "strong": pg.image.load('assets/images/nemesis/nemesis_3.png').convert_alpha(),
        "elite": pg.image.load('assets/images/nemesis/nemesis_4.png').convert_alpha()
    }
    buy_tower_image = pg.image.load('assets/images/buttons/buy_watchtower.png').convert_alpha()
    cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
    upgrade_tower_image = pg.image.load('assets/images/buttons/upgrade_watchtower.png').convert_alpha()
    begin_image = pg.image.load('assets/images/buttons/start.png').convert_alpha()
    restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
    fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
    heart_image = pg.image.load("assets/images/ui/heart.png").convert_alpha()
    coin_image = pg.image.load("assets/images/ui/coin.png").convert_alpha()
    logo_image = pg.image.load("assets/images/ui/logo.png").convert_alpha()
except pg.error as e:
    print(f"Error loading images: {e}")
    pg.quit()
   

# Load sound effects
try:
    shot_fx = pg.mixer.Sound('assets/audio/watchtower_shot.wav')
    shot_fx.set_volume(0.5)
except pg.error as e:
    print(f"Error loading sound: {e}")
    pg.quit()
   

# Load level data from JSON
try:
    with open('assets/images/levels/level.tmj') as file:
        world_data = json.load(file)
except FileNotFoundError as e:
    print(f"Level file not found: {e}")
    pg.quit()
   
except json.JSONDecodeError as e:
    print(f"Invalid JSON in level file: {e}")
    pg.quit()
   

# Load fonts
try:
    text_font = pg.font.SysFont("Cousine", 24, bold=True)
    large_font = pg.font.SysFont("Cousine", 36)
except pg.error as e:
    print(f"Error loading fonts: {e}")
    pg.quit()
   

# Function to render text on screen
def draw_text(text, font, color, x, y):
    try:
        img = font.render(text, True, color)
        screen.blit(img, (x, y))
    except:
        print(f"Error rendering the text on screen.")

# Function to display game stats on side panel
def display_data():
    try:
        pg.draw.rect(screen, "lightblue", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
        pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
        screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
        draw_text(f"LEVEL: {world.level}", text_font, "black", c.SCREEN_WIDTH + 100, 10)
        screen.blit(heart_image, (c.SCREEN_WIDTH - 700, 0))
        draw_text(str(world.health), text_font, "red", c.SCREEN_WIDTH - 650, 7)
        screen.blit(coin_image, (c.SCREEN_WIDTH - 700, 30))
        draw_text(str(world.money), text_font, "red", c.SCREEN_WIDTH - 650, 30)
    except:
        print(f"Error displaying game statistics on screen.")

# Function to place a watchtower at mouse position
def create_watchtower(mouse_pos):
    try:
        tile_x = mouse_pos[0] // c.TILE_SIZE
        tile_y = mouse_pos[1] // c.TILE_SIZE
        tile_num = (tile_y * c.COLS) + tile_x
        if world.tile_map[tile_num] == 7:
            if all((tile_x, tile_y) != (tower.tile_x, tower.tile_y) for tower in watchtower_group):
                new_watchtower = WatchTower(watchtower_spritesheets, tile_x, tile_y, shot_fx)
                watchtower_group.add(new_watchtower)
                world.money -= c.BUY_COST
    except:
        print(f"Error placing the Watch Tower.")

# Function to select a watchtower at mouse position
def select_watchtower(mouse_pos):
    try:
        tile_x = mouse_pos[0] // c.TILE_SIZE
        tile_y = mouse_pos[1] // c.TILE_SIZE
        for tower in watchtower_group:
            if (tile_x, tile_y) == (tower.tile_x, tower.tile_y):
                return tower
        return None
    except:
        print(f"Error in selecting the Watch Tower.")

# Function to deselect all watchtowers
def clear_selection():
    for tower in watchtower_group:
            tower.selected = False

# Initialize game world
try:
    world = GameManager(world_data, map_image)
    world.process_data()
    world.process_nemesis()
except Exception as e:
    print(f"Error creating world: {e}")
    pg.quit()

# Create sprite groups
nemesis_group = pg.sprite.Group()
watchtower_group = pg.sprite.Group()

# Create UI buttons
try:
    watchtower_button = UIManager(c.SCREEN_WIDTH + 77, 120, buy_tower_image, True)
    cancel_button = UIManager(c.SCREEN_WIDTH + 77, 180, cancel_image, True)
    upgrade_button = UIManager(c.SCREEN_WIDTH + 77, 280, upgrade_tower_image, True)
    begin_button = UIManager(c.SCREEN_WIDTH + 77, 340, begin_image, True)
    restart_button = UIManager(310, 340, restart_image, True)
    fast_forward_button = UIManager(c.SCREEN_WIDTH + 77, 340, fast_forward_image, False)
except ValueError as e:
    print(f"Error creating buttons: {e}")
    pg.quit()

# Main game loop
run = True
while run:
    try:
        clock.tick(c.FPS)
    except AttributeError as e:
        print(f"Error with FPS value: {e}")
        run = False

    if game_state == "menu":
        action = menu.run()
        if action == "start":
            game_state = "playing"
        elif action == "exit":
            run = False
    elif game_state == "playing":
        # Update game state
        if not game_over:
            if world.health <= 0:
                game_over, game_outcome = True, -1
            elif world.level > c.TOTAL_LEVELS:
                game_over, game_outcome = True, 1
            else:
                nemesis_group.update(world)
                watchtower_group.update(nemesis_group, world)
                if selected_watchtower:
                    selected_watchtower.selected = True

        # Render game elements
        try:
            world.draw(screen)
            nemesis_group.draw(screen)
            for tower in watchtower_group:
                tower.draw(screen)
            display_data()
        except pg.error as e:
            print(f"Error drawing game elements: {e}")
            run = False

        if not game_over:
            if not level_started:
                if begin_button.draw(screen):
                    level_started = True
            else:
                world.game_speed = 1
                if fast_forward_button.draw(screen):
                    world.game_speed = 2
                if pg.time.get_ticks() - last_nemesis_spawn > c.SPAWN_COOLDOWN:
                    if world.spawned_nemesis < len(world.nemesis_list):
                        nemesis_type = world.nemesis_list[world.spawned_nemesis]
                        nemesis = Nemesis(nemesis_type, world.waypoints, nemesis_images)
                        nemesis_group.add(nemesis)
                        world.spawned_nemesis += 1
                        last_nemesis_spawn = pg.time.get_ticks()

                if world.check_level_complete():
                    world.money += c.LEVEL_COMPLETE_REWARD
                    world.level += 1
                    level_started = False
                    last_nemesis_spawn = pg.time.get_ticks()
                    world.reset_level()
                    world.process_nemesis()

            draw_text("COST TO BUY:", text_font, "black", c.SCREEN_WIDTH + 15, 80)
            draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 175, 80)
            screen.blit(coin_image, (c.SCREEN_WIDTH + 230, 75))
            if watchtower_button.draw(screen):
                placing_watchtower = True
            if placing_watchtower:
                cursor_rect = cursor_watchtower.get_rect()
                cursor_pos = pg.mouse.get_pos()
                cursor_rect.center = cursor_pos
                if cursor_pos[0] <= c.SCREEN_WIDTH:
                    screen.blit(cursor_watchtower, cursor_rect)
                if cancel_button.draw(screen):
                    placing_watchtower = False
            if selected_watchtower and selected_watchtower.level < c.WATCHTOWER_LEVELS:
                draw_text("COST TO UPGRADE:", text_font, "black", c.SCREEN_WIDTH + 15, 250)
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 190, 250)
                screen.blit(coin_image, (c.SCREEN_WIDTH + 230, 245))
                if upgrade_button.draw(screen) and world.money >= c.UPGRADE_COST:
                    selected_watchtower.upgrade()
                    world.money -= c.UPGRADE_COST
        else:
            pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius=30)
            draw_text("GAME OVER" if game_outcome == -1 else "YOU WIN!", large_font, "grey0", 310, 230)
            if restart_button.draw(screen):
                game_over, level_started, placing_watchtower = False, False, False
                selected_watchtower = None
                last_nemesis_spawn = pg.time.get_ticks()
                world = GameManager(world_data, map_image)
                world.process_data()
                world.process_nemesis()
                nemesis_group.empty()
                watchtower_group.empty()

        # Handle events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                    selected_watchtower = None
                    clear_selection()
                    if placing_watchtower and world.money >= c.BUY_COST:
                        create_watchtower(mouse_pos)
                    else:
                        selected_watchtower = select_watchtower(mouse_pos)

    # Update display
    try:
        pg.display.flip()
    except pg.error as e:
        print(f"Error updating display: {e}")
        run = False

# Cleanup and exit
pg.quit()