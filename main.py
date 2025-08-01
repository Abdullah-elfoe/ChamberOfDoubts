import pygame
import pygame_gui
from ui.layouts.HomeScreen import MainMenu
from config import general

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(general.WINDOW_NAME)

# GUI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Menu instance (Independent of game engine!)
menu = MainMenu(manager, WIDTH, HEIGHT)

clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        menu.handle_event(event)
        manager.process_events(event)

    menu.update(time_delta)

    window.fill((30, 30, 30))  # Dark background
    menu.draw(window)
    manager.draw_ui(window)
    pygame.display.flip()

pygame.quit()
