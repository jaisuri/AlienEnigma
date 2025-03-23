import pygame as pg
import json
from nemesis import Nemesis
from gamemanager import GameManager
from watchtower import WatchTower
from uimanager import UIManager
import settings as c

# Initialize pygame
try:
    pg.init()
except Exception as e:
    print(f"Failed to initialize Pygame: {e}")
    pg.quit()

# Create clock for frame rate control
clock = pg.time.Clock()

# Create game window
try:
    screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.display.set_caption("Alien Enigma")
except AttributeError as e:
    print(f"Invalid screen dimensions in constants: {e}")
    pg.quit()
    
except pg.error as e:
    print(f"Failed to create game window: {e}")
    pg.quit()
    

# Game variables
game_over = False  # Flag for game over state
game_outcome = 0  # -1 is loss, 1 is win
level_started = False  # Flag for level start
last_enemy_spawn = pg.time.get_ticks()  # Time of last enemy spawn
placing_watchtower = False  # Flag for watch tower placement mode
selected_watchtower = None  # Currently selected watch tower

# Load images
try:
    # Map image
    map_image = pg.image.load('levels/level.png').convert_alpha()
    # Watchtower spritesheets
    turret_spritesheets = []
    for x in range(1, c.WATCHTOWER_LEVELS + 1):
        turret_sheet = pg.image.load(f'assets/images/watchtowers/turret_{x}.png').convert_alpha()
        turret_spritesheets.append(turret_sheet)
    # Cursor watch tower image
    cursor_watchtower = pg.image.load('assets/images/watchtowers/cursor_turret.png').convert_alpha()
    # Enemy images
    enemy_images = {
        "weak": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
        "medium": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
        "strong": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
        "elite": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha()
    }
    # Button images
    buy_tower_image = pg.image.load('assets/images/buttons/buy_tower.png').convert_alpha()
    cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
    upgrade_tower_image = pg.image.load('assets/images/buttons/upgrade_tower.png').convert_alpha()
    begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()
    restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
    fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
    # GUI images
    heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
    coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()
    logo_image = pg.image.load("assets/images/gui/logo.png").convert_alpha()
except pg.error as e:
    print(f"Error loading images: {e}")
    pg.quit()
    

# Load sounds
try:
    shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
    shot_fx.set_volume(0.5)
except pg.error as e:
    print(f"Error loading sound: {e}")
    pg.quit()
    

# Load json data for level
try:
    with open('levels/level.tmj') as file:
        world_data = json.load(file)
except FileNotFoundError as e:
    print(f"Level file not found: {e}")
    pg.quit()
    
except json.JSONDecodeError as e:
    print(f"Invalid JSON in level file: {e}")
    pg.quit()
    

# Load fonts for displaying text on the screen
try:
    text_font = pg.font.SysFont("Cousine", 24, bold=True)
    large_font = pg.font.SysFont("Cousine", 36)
except pg.error as e:
    print(f"Error loading fonts: {e}")
    pg.quit()
    

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    try:
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))
    except AttributeError as e:
        print(f"Error rendering text: {e}")
    except pg.error as e:
        print(f"Pygame error blitting text: {e}")

def display_data():
    # Display game data on the side panel
    try:
        # Draw panel
        pg.draw.rect(screen, "lightblue", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
        pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
        screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
        # Display data
        draw_text("LEVEL: " + str(world.level), text_font, "black", c.SCREEN_WIDTH + 100, 10)
        screen.blit(heart_image, (c.SCREEN_WIDTH -700, 0))
        draw_text(str(world.health), text_font, "red", c.SCREEN_WIDTH - 650, 7)
        screen.blit(coin_image, (c.SCREEN_WIDTH -700, 30))
        draw_text(str(world.money), text_font, "red", c.SCREEN_WIDTH - 650, 30)
    except AttributeError as e:
        print(f"Error displaying data: {e}")
    except pg.error as e:
        print(f"Pygame error in display_data: {e}")

def create_watchtower(mouse_pos):
    # Place a watch tower at the mouse position if valid
    try:
        mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
        mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
        mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
        if world.tile_map[mouse_tile_num] == 7:  # Grass tile
            space_is_free = True
            for watchtower in watchtower_group:
                if (mouse_tile_x, mouse_tile_y) == (watchtower.tile_x, watchtower.tile_y):
                    space_is_free = False
            if space_is_free:
                new_turret = WatchTower(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
                watchtower_group.add(new_turret)
                world.money -= c.BUY_COST
    except IndexError as e:
        print(f"Error placing watch tower: Invalid tile index {e}")
    except AttributeError as e:
        print(f"Error with watchtower creation: {e}")

def select_watchtower(mouse_pos):
    # Select a watchtower  at the mouse position
    try:
        mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
        mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
        for watchtower in watchtower_group:
            if (mouse_tile_x, mouse_tile_y) == (watchtower.tile_x, watchtower.tile_y):
                return watchtower
    except AttributeError as e:
        print(f"Error selecting watch tower: {e}")
    return None

def clear_selection():
    # Clear selection of all turrets
    try:
        for watchtower in watchtower_group:
            watchtower.selected = False
    except AttributeError as e:
        print(f"Error clearing selection: {e}")

# Create world
try:
    world = GameManager(world_data, map_image)
    world.process_data()
    world.process_enemies()
except Exception as e:
    print(f"Error creating world: {e}")
    pg.quit()
    

# Create groups
enemy_group = pg.sprite.Group()
watchtower_group = pg.sprite.Group()

# Create buttons
try:
    turret_button = UIManager(c.SCREEN_WIDTH + 77, 120, buy_tower_image, True)
    cancel_button = UIManager(c.SCREEN_WIDTH + 77, 180, cancel_image, True)
    upgrade_button = UIManager(c.SCREEN_WIDTH + 5, 180, upgrade_tower_image, True)
    begin_button = UIManager(c.SCREEN_WIDTH + 77, 300, begin_image, True)
    restart_button = UIManager(310, 300, restart_image, True)
    fast_forward_button = UIManager(c.SCREEN_WIDTH + 77, 300, fast_forward_image, False)
except ValueError as e:
    print(f"Error creating buttons: {e}")
    pg.quit()
    

# Game loop
run = True
while run:
    try:
        clock.tick(c.FPS)
    except AttributeError as e:
        print(f"Error with FPS value: {e}")
        run = False

    # UPDATING SECTION
    if not game_over:
        # Check if player has lost
        if world.health <= 0:
            game_over = True
            game_outcome = -1  # Loss
        # Check if player has won
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1  # Win

        # Update groups
        try:
            enemy_group.update(world)
            watchtower_group.update(enemy_group, world)
        except Exception as e:
            print(f"Error updating groups: {e}")

        # Highlight selected watch tower
        if selected_watchtower:
            try:
                selected_watchtower.selected = True
            except AttributeError as e:
                print(f"Error highlighting watch tower: {e}")

    # DRAWING SECTION
    try:
        world.draw(screen)
        enemy_group.draw(screen)
        for watchtower in watchtower_group:
            watchtower.draw(screen)
        display_data()
    except pg.error as e:
        print(f"Error drawing game elements: {e}")
        run = False

    if not game_over:
        # Check if level has started
        if not level_started:
            if begin_button.draw(screen):
                level_started = True
        else:
            # Fast forward option
            world.game_speed = 1
            if fast_forward_button.draw(screen):
                world.game_speed = 2
            # Spawn enemies
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                try:
                    if world.spawned_enemies < len(world.enemy_list):
                        enemy_type = world.enemy_list[world.spawned_enemies]
                        nemesis = Nemesis(enemy_type, world.waypoints, enemy_images)
                        enemy_group.add(nemesis)
                        world.spawned_enemies += 1
                        last_enemy_spawn = pg.time.get_ticks()
                except KeyError as e:
                    print(f"Invalid enemy type: {e}")
                except AttributeError as e:
                    print(f"Error spawning enemy: {e}")

        # Check if wave is finished
        try:
            if world.check_level_complete():
                world.money += c.LEVEL_COMPLETE_REWARD
                world.level += 1
                level_started = False
                last_enemy_spawn = pg.time.get_ticks()
                world.reset_level()
                world.process_enemies()
        except Exception as e:
            print(f"Error checking level completion: {e}")

        # Draw buttons
        try:
            draw_text("COST TO BUY :", text_font, "black", c.SCREEN_WIDTH + 15, 80)
            draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 175, 80)
            screen.blit(coin_image, (c.SCREEN_WIDTH + 230, 75))
            if turret_button.draw(screen):
                placing_watchtower = True
            if placing_watchtower:
                cursor_rect = cursor_watchtower.get_rect()
                cursor_pos = pg.mouse.get_pos()
                cursor_rect.center = cursor_pos
                if cursor_pos[0] <= c.SCREEN_WIDTH:
                    screen.blit(cursor_watchtower, cursor_rect)
                if cancel_button.draw(screen):
                    placing_turrets = False
            if selected_watchtower:
                if selected_turret.upgrade_level < c.WATCHTOWER_LEVELS:
                    draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
                    screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
                    if upgrade_button.draw(screen):
                        if world.money >= c.UPGRADE_COST:
                            selected_turret.upgrade()
                            world.money -= c.UPGRADE_COST
        except pg.error as e:
            print(f"Error drawing buttons: {e}")
    else:
        try:
            pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius=30)
            if game_outcome == -1:
                draw_text("GAME OVER", large_font, "grey0", 310, 230)
            elif game_outcome == 1:
                draw_text("YOU WIN!", large_font, "grey0", 315, 230)
            if restart_button.draw(screen):
                game_over = False
                level_started = False
                placing_turrets = False
                selected_turret = None
                last_enemy_spawn = pg.time.get_ticks()
                world = World(world_data, map_image)
                world.process_data()
                world.process_enemies()
                enemy_group.empty()
                watchtower_group.empty()
        except pg.error as e:
            print(f"Error drawing game over screen: {e}")

    # Event handler
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            try:
                mouse_pos = pg.mouse.get_pos()
                if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                    selected_turret = None
                    clear_selection()
                    if placing_watchtower and world.money >= c.BUY_COST:
                        create_watchtower(mouse_pos)
                    else:
                        selected_turret = select_watchtower(mouse_pos)
            except pg.error as e:
                print(f"Error handling mouse click: {e}")

    # Update display
    try:
        pg.display.flip()
    except pg.error as e:
        print(f"Error updating display: {e}")
        run = False

# Cleanup and quit
try:
    pg.quit()
except Exception as e:
    print(f"Error quitting Pygame: {e}")