import pygame
import pygame_gui
from HomeScreen import Main, text_surface
from gametempate import Template
from config.ui import MARGIN
from config.general import WINDOW_NAME


pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_NAME)

background = pygame.image.load("assets/images/general/background.jpg").convert()
background = pygame.transform.scale(background, (800, 600))


manager = pygame_gui.UIManager((WIDTH, HEIGHT), r"D:\ChamberOfDoubts\assets\themes.json")
HomeScreen = Main(manager)
# game = Template(manager)

clock = pygame.time.Clock()
running = True





while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        HomeScreen.detectModes(event)
        HomeScreen.detectInput(event)
        # HomeScreen.handle_event(event)
        manager.process_events(event)

    HomeScreen.update(time_delta)

    window.fill((30, 30, 30))  # Dark background
    # HomeScreen.draw(window)
    window.blit(background, (0, 0))
    if not HomeScreen.terminated:
        window.blit(text_surface, (MARGIN, 350))
    manager.draw_ui(window)
    pygame.display.flip()

pygame.quit()
