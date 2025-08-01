""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../')))
""" Reseting the root diretory manually"""


import pygame
from logic import Game, logic
from ui.layoutManager import Manager
from ui.layouts.GameScreen import Template as gameTemplate
from ui.layouts.Home2 import Template as homeTemplate
from ui.Animations.MatchMaking import MatchmakingDots
from scripts.Networking import P2PNetwork
from config import general
from json import loads





class Main(Game):
    def __init__(self):
        self.home = homeTemplate()
        self.game = gameTemplate()
        self.theMainscreen = None
        self.game.MainRef = self
        self.loadingScreen = MatchmakingDots((540,general.WINDOW_HEIGHT-40), 10, 30)
        self.homeScreenNo = 1
        self.gameScreenNo = 2
        self.loadingScreenNo = 0
        self.loading = False
        self.home.setMainRef(self)
        super().__init__(self.game)
        self.UImanager = Manager([self.loadingScreen,self.home,self.game])
        self.UImanager.showScreenNo(self.homeScreenNo)








if __name__=="__main__":
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800, 600))
    pygame.init()
    pygame.font.init()
    ChamberOfDoubts = Main()
    ChamberOfDoubts.theMainscreen = screen
    running = True
    counter = 0
    
    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()

        # if ChamberOfDoubts.home.visible and ChamberOfDoubts.network.is_connected and not ChamberOfDoubts.ishost:
        #     ChamberOfDoubts.UImanager.showScreen(ChamberOfDoubts.gameScreenNo)

        messages = ChamberOfDoubts.network.get_received_messages()
        
        for msg in messages:
            if msg['type'] == 'chat':
                ChamberOfDoubts.game.notebook.addToNotebook("Chats", ChamberOfDoubts.home.connectScreen.ipAdress,msg['content'])
            elif msg['type'] == "game":
                inv = msg['content'].get("Opponent Inventory")
                if inv is not None:
                    if not ChamberOfDoubts.game.opponentInventory.isEmpty:
                        ChamberOfDoubts.game.opponentInventory.clear()
                    for item, qty in inv:
                        if qty != 0:
                            ChamberOfDoubts.game.opponentInventory.addToInventory(item, qty)
                myturn = msg['content'].get("myTurn")
                opponentTurn = msg['content'].get("opponentTurn")
                bullets = msg['content'].get("bullets")
                o_HB = msg['content'].get("opponentHB")
                m_HB = msg['content'].get("myHB")
                myinv = msg['content'].get("My Inventory")
                if (myturn is not None) and (opponentTurn is not None):
                    ChamberOfDoubts.opponentTurn = myturn
                    ChamberOfDoubts.myTurn = opponentTurn
                if bullets is not None:
                    ChamberOfDoubts.bullets = bullets
                if (o_HB is not None) and (m_HB is not None):
                    ChamberOfDoubts.game.myHealthBar.current_health = o_HB
                    ChamberOfDoubts.game.opponentHealthBar.current_health = m_HB
                    # counter += 1
                    # switched = content.get("switched")
                if myinv is not None:
                    print("Not None Items are there")
                    if not ChamberOfDoubts.game.myInventory.isEmpty:
                        print("Not emtpy either")
                        ChamberOfDoubts.game.myInventory.clear()
                    for item, qty in myinv:
                        if qty != 0:
                            ChamberOfDoubts.game.myInventory.addToInventory(item, qty)
                        print(item, qty, "HERE")
                    print("here", ChamberOfDoubts.myTurn, ChamberOfDoubts.opponentTurn, counter)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ChamberOfDoubts.home.handleEvent(event)
            ChamberOfDoubts.game.handleEvent(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print(ChamberOfDoubts.bullets)
          

            

        for function in ChamberOfDoubts.temporaryFunctions:
            if ChamberOfDoubts.game.visible:
                function()
                ChamberOfDoubts.temporaryFunctions.remove(function)
        ChamberOfDoubts.home.update(mouse_pos, dt)
        ChamberOfDoubts.game.update(mouse_pos, dt)
        screen.fill((30, 30, 30))
        screen.blit(ChamberOfDoubts.UImanager.background)
        ChamberOfDoubts.home.manage()
        ChamberOfDoubts.game.manage()
        ChamberOfDoubts.home.draw(screen)
        ChamberOfDoubts.game.draw(screen)
        ChamberOfDoubts.loadingScreen.draw(screen)
        ChamberOfDoubts.UImanager.update()
        # ChamberOfDoubts.network.update()
        ChamberOfDoubts.play()
        pygame.display.flip()



        if ChamberOfDoubts.game.gun.permission and ChamberOfDoubts.game.myInventory.permission:
            ChamberOfDoubts.game.myInventory.permission = False
        elif not ChamberOfDoubts.game.gun.permission and not ChamberOfDoubts.game.myInventory.permission:
            ChamberOfDoubts.game.gun.permission = True
            ChamberOfDoubts.game.opponentInventory.permission = True

    pygame.quit()
