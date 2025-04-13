# UIManager class for Alien Enigma
# Makes buttons for stuff like buying watchtowers or starting nemesis waves

import pygame

class UIManager:
    def __init__(self, x, y, button_image, one_shot):
        # Set up a button with where it goes and what it looks like
        try:
            self.image = button_image       # Picture for the button
            self.rect = button_image.get_rect(topleft=(x, y))  # Where to put it
            self.is_clicked = False         # Keeps track of clicks
            self.one_shot = one_shot        # True for buttons that only click once
        except:
            print(f"Error initialising the UI Manager")


    def draw(self, screen):
        # Show the button and check if it's clicked
        got_clicked = False
        try:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                if not self.is_clicked:
                    got_clicked = True
                    if self.one_shot:
                        self.is_clicked = True
            # Only stay clicked if the mouse is still down
            self.is_clicked = self.is_clicked and pygame.mouse.get_pressed()[0]
            screen.blit(self.image, self.rect)
        except pygame.error:
            print("Something went wrong drawing the button!")
        return got_clicked