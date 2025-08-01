import pygame
import pygame_gui
from HomeScreen import Main, text_surface
from ui.layouts.GameScreen import Template
from config.ui import MARGIN
from config.general import WINDOW_NAME, WINDOW_HEIGHT, WINDOW_WIDTH
from config import sounds
from scripts.logic import logic, Game

pygame.init()

# Window setup
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_NAME)

background = pygame.image.load("assets/images/general/background.jpg").convert()
background = pygame.transform.scale(background, (800, 600))


manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), r"D:\ChamberOfDoubts\assets\themes.json")
HomeScreen = Main(manager)
# game = Template(manager)

clock = pygame.time.Clock()
running = True




started = False
template = Template(object)
game = Game(template)
game.template.myInventory.toggle()

while running:
    time_delta = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()
    pressed = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        HomeScreen.detectModes(event)
        HomeScreen.detectInput(event)
        # HomeScreen.handle_event(event)
        manager.process_events(event)
        template.PlayerSelectionPanel.handle_event(event, [sounds.CLICK.play])
        template.infoBooth.handle_event(event)
    window.fill((30, 30, 30))  # Dark background
    window.blit(background, (0, 0))

    HomeScreen.update(time_delta)
    if HomeScreen.play:
        HomeScreen.terminate()
        game.play()
        logic(template, mouse_pos, pressed, window)
        if game.gameOver:
            HomeScreen.play = False

    # HomeScreen.draw(window)
    if not HomeScreen.terminated:
        window.blit(text_surface, (MARGIN, 350))
    manager.draw_ui(window)
    pygame.display.flip()

pygame.quit()
