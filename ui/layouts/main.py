import pygame
import pygame_gui
from menu import MainMenu
from scripts.game_engine import GameEngine

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chamber of Doubts")

# GUI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Game State
menu = MainMenu(manager, WIDTH, HEIGHT)
game = GameEngine()

clock = pygame.time.Clock()
running = True
in_game = False

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if in_game:
            game.handle_event(event)
        else:
            menu.handle_event(event)

        manager.process_events(event)

    if in_game:
        game.update(time_delta)
    else:
        menu.update(time_delta)

    window.fill((0, 0, 0))

    if in_game:
        game.draw(window)
    else:
        menu.draw(window)

    manager.draw_ui(window)
    pygame.display.flip()

pygame.quit()
