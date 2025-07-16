import pygame
import pygame_gui
from HomeScreen import Main


pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("test")

# GUI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# HomeScreen instance (Independent of game engine!)
HomeScreen = Main(manager, WIDTH, HEIGHT)

clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        HomeScreen.detectModes(event)
        # HomeScreen.handle_event(event)
        manager.process_events(event)

    HomeScreen.update(time_delta)

    window.fill((30, 30, 30))  # Dark background
    # HomeScreen.draw(window)

    manager.draw_ui(window)
    pygame.display.flip()

pygame.quit()
