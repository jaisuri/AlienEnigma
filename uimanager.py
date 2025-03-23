import pygame as pg

class UIManager():
    def __init__(self, x, y, image, single_click):
        # Initialize a button with position, image, and click behavior
        try:
            self.image = image  # Pygame Surface for the button image
            self.rect = self.image.get_rect()  # Rectangle for collision and positioning
            self.rect.topleft = (x, y)  # Set button position
            self.clicked = False  # Track if button is currently clicked
            self.single_click = single_click  # Boolean to determine if button is single-click only
        except AttributeError as e:
            raise ValueError(f"Invalid image provided: {e}")
        except TypeError as e:
            raise TypeError(f"Invalid x, y, or single_click parameters: {e}")

    def draw(self, surface):
        # Draw the button on the surface and handle click events
        action = False  # Return value indicating if button was clicked
        
        try:
            # Get mouse position
            pos = pg.mouse.get_pos()
        except pg.error as e:
            print(f"Error getting mouse position: {e}")
            return action

        try:
            # Check mouseover and clicked conditions
            if self.rect.collidepoint(pos):
                if pg.mouse.get_pressed()[0] == 1 and not self.clicked:
                    action = True
                    # If button is a single-click type, mark it as clicked
                    if self.single_click:
                        self.clicked = True
        except IndexError as e:
            print(f"Error checking mouse buttons: {e}")
        except AttributeError as e:
            print(f"Error with rect or collision check: {e}")

        # Reset clicked state when mouse button is released
        try:
            if pg.mouse.get_pressed()[0] == 0:
                self.clicked = False
        except IndexError as e:
            print(f"Error checking mouse release: {e}")

        # Draw button on screen
        try:
            surface.blit(self.image, self.rect)
        except TypeError as e:
            print(f"Error drawing button: Invalid surface or image: {e}")
        except pg.error as e:
            print(f"Pygame error drawing button: {e}")

        return action