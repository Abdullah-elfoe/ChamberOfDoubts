import pygame


""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../')))
""" Reseting the root diretory manually"""

from config import general, ui
from .Animations import MatchMaking
from scripts.timer import Timer
from .layouts import GameScreen, Home2
import pygame




class Manager:
    def __init__(self, screens:list):
        self.screens = screens
        self.visible = 1
        background = pygame.image.load("assets/images/general/background.jpg").convert()
        self.background = pygame.transform.scale(background, (800, 600))
        self.screenTimer = Timer(0, 300)
        self.animationRunning = False
        self.data = None

    def showScreenNo(self, number):
        self.visible = number
        self.manage()

    def manage(self):
        for i, screen in enumerate(self.screens):
            if i == self.visible:
                screen.show()
            else:
                screen.hide()

    def update(self):
        if not self.screenTimer.finished:
            self.screenTimer.start
            if self.screenTimer.pointer+1 == self.screenTimer.stop_time:
                self.showScreenNo(self.visible)
                if not self.data is None:
                    self.screens[self.visible].data = self.data


    def showScreen(self, screen):
        self.data = self.screens[screen].data
        self.screenTimer.start
        self.showScreenNo(0)
        self.visible = screen



if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Comic Sans MS", 30)
    home = Home2.Template()
    game = GameScreen.Template()
    matchmaking = MatchMaking.MatchmakingDots((540,general.WINDOW_HEIGHT-40), 10, 30)
    manager = Manager([matchmaking, home, game])
    game.opponentInventory.addToInventory("Glasses")


    running = True
    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            home.handleEvent(event)
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_1:
                    manager.showScreenNo(1)
                elif event.key == pygame.K_2:
                    manager.showScreenNo(2)
                else:
                    manager.showScreenNo(0)

            


        home.update(mouse_pos, dt)
        game.update(mouse_pos, dt)
        screen.fill((30, 30, 30))
        screen.blit(manager.background)
        home.manage()
        game.manage()
        home.draw(screen)
        game.draw(screen)
        matchmaking.draw(screen)
        
        # print(game.controls.permission)
        pygame.display.flip()
    pygame.quit()