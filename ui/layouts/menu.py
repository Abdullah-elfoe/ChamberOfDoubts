import pygame
import pygame_gui

class MainMenu:
    def __init__(self, manager, width, height):
        self.manager = manager

        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((width//2 - 150, 100), (300, 50)),
            text='Chamber of Doubts',
            manager=manager
        )

        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width//2 - 75, height//2 - 50), (150, 50)),
            text='Start Game',
            manager=manager
        )

        self.settings_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width//2 - 75, height//2 + 10), (150, 50)),
            text='Settings',
            manager=manager
        )

        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width//2 - 75, height//2 + 70), (150, 50)),
            text='Quit',
            manager=manager
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_button:
                print("[Menu] Start Game Clicked (no game engine tied yet)")
            elif event.ui_element == self.settings_button:
                print("[Menu] Settings Clicked")
            elif event.ui_element == self.quit_button:
                print("[Menu] Quit Clicked")
                exit()

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self, window):
        pass  # GUI draws itself
