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
from config.ui import MARGIN
from bots.base import PrimaryLayer




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


def managePositionsofWidgets(instance, fullscreen):
    instance.home.gameDescription.rect.y = general.WINDOW_HEIGHT-(general.WINDOW_HEIGHT//3)
    instance.home.gameName.pos = (MARGIN, general.WINDOW_HEIGHT-(general.WINDOW_HEIGHT//3)-60)
    instance.home.playButton.base_rect.y = general.WINDOW_HEIGHT-instance.home.playButton.base_rect.height-MARGIN
    instance.home.exitButton.base_rect.y = general.WINDOW_HEIGHT-instance.home.playButton.base_rect.height-MARGIN
    instance.game.opponentHealthBar.pos = (MARGIN, general.WINDOW_HEIGHT-general.HEALTHBAR_HEIGHT-MARGIN)
    instance.game.myHealthBar.pos = (general.WINDOW_WIDTH-general.HEALTHBAR_WIDTH-MARGIN, general.WINDOW_HEIGHT-general.HEALTHBAR_HEIGHT-MARGIN)
    instance.game.opponentInventory.resetPosition([general.WINDOW_WIDTH//2-(general.SQUAREINVENTORY_WIDTH//2), "MOYE MOYE MOYE MOYE OYE MOYE"], fullscreen)
    instance.game.controls.resetCenter((general.WINDOW_WIDTH//2, general.WINDOW_HEIGHT-general.CONTROLPANEL_SIZE//2-MARGIN))
    ChamberOfDoubts.game.gun.pos = (general.WINDOW_WIDTH//2+70, general.WINDOW_HEIGHT//2)
  
    # instance.game.myInventory.y = 






def toggleFullScreen(fullScreen, instance):
    global managePositionsofWidgets
    if fullScreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((800, 600))
         # Update screen size
    general.WINDOW_WIDTH, general.WINDOW_HEIGHT  = screen.get_size()

    # Rescale background
    # background = pygame.image.load(instance.UImanager.background).convert()
    background = pygame.transform.scale(instance.UImanager.background, (general.WINDOW_WIDTH, general.WINDOW_HEIGHT))
    managePositionsofWidgets(instance, fullScreen)
    return screen, background



if __name__=="__main__":
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((general.WINDOW_WIDTH, general.WINDOW_HEIGHT))
    pygame.init()
    pygame.font.init()
    ChamberOfDoubts = Main()
    ChamberOfDoubts.theMainscreen = screen
    running = True
    counter = 0
    fullScreen = False
    background = ChamberOfDoubts.UImanager.background

    # screen, background = toggleFullScreen(fullScreen, ChamberOfDoubts)
    
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
                o_mHB = msg['content'].get("opponentmHB")
                m_mHB = msg['content'].get("mymHB")
                myinv = msg['content'].get("My Inventory")
                phase = msg['content'].get("phase")
                gameOver = msg['content'].get("gameOver")
                used = msg['content'].get("used")

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
                if o_mHB is not None:
                    print("I am here!!!")
                    ChamberOfDoubts.game.myHealthBar.max_health = o_mHB
                    ChamberOfDoubts.game.opponentHealthBar.max_health = m_mHB
                    ChamberOfDoubts.game.myHealthBar.current_health = o_mHB
                    ChamberOfDoubts.game.opponentHealthBar.current_health = m_mHB 
                if phase:
                    ChamberOfDoubts.currentPhase = phase
                    ChamberOfDoubts.game.popup.display("Level "+str(phase))
        

                if used:
                    ChamberOfDoubts.game.popup.display(f"{used}")
                if gameOver:
                    ChamberOfDoubts.gameOver = True
        if not ChamberOfDoubts.gameOver:
            ChamberOfDoubts.play()
        else:
            # print("HI")
            if not ChamberOfDoubts.game.popup.visible:
                # print("HI", 2)
                ChamberOfDoubts.gameOver = False
                ChamberOfDoubts.home.bots.permission = True
                ChamberOfDoubts.myTurn = False
                ChamberOfDoubts.opponentTurn = False
                ChamberOfDoubts.network.send_game({'gameOver':True})

                # ChamberOfDoubts.game.myInventory.addToInventory("Bazuka", 38)
                ChamberOfDoubts.UImanager.showScreenNo(ChamberOfDoubts.homeScreenNo)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ChamberOfDoubts.home.handleEvent(event)
            ChamberOfDoubts.game.handleEvent(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    del ChamberOfDoubts
                    from sys import exit as _________________
                    _________________()
                    break
                if event.key == pygame.K_F11:
                    fullScreen = not fullScreen
                    screen, background = toggleFullScreen(fullScreen, ChamberOfDoubts)
                if event.key == pygame.K_SPACE:
                    print(ChamberOfDoubts.currentPhase)
                    print(ChamberOfDoubts.game.PlayerSelectionPanel.permission)
                    print(ChamberOfDoubts.myTurn, ChamberOfDoubts.opponentTurn)
                    # print(ChamberOfDoubts.bullets, len(ChamberOfDoubts.bullets))
                    # print(PrimaryLayer.bullets, len(PrimaryLayer.bullets))
                    # print(PrimaryLayer.blanks, "blanks", PrimaryLayer.live, "live")
                    # # print(ChamberOfDoubts.game.opponentInventory.getItems())
                    # ChamberOfDoubts.game.opponentInventory.addToInventory("Bazuka", 118)
                if event.key == pygame.K_LALT:
                    # ChamberOfDoubts.game.opponentInventory.x += 20
                    print()
                    # for _099 in ChamberOfDoubts.game.opponentInventory.inventory:
                     
                    # #     _099.rect.x += 20
                    
                    #     print(_099.x)


                    # print(ChamberOfDoubts.game.opponentInventory.getItems())

            

        for function in ChamberOfDoubts.temporaryFunctions:
            if ChamberOfDoubts.game.visible:
                function()
                ChamberOfDoubts.temporaryFunctions.remove(function)
        ChamberOfDoubts.home.update(mouse_pos, dt)
        ChamberOfDoubts.game.update(mouse_pos, dt)
        screen.fill((30, 30, 30))
        screen.blit(background, (0, 0))
        ChamberOfDoubts.home.manage()
        ChamberOfDoubts.game.manage()
        ChamberOfDoubts.home.draw(screen)
        ChamberOfDoubts.game.draw(screen)
        ChamberOfDoubts.loadingScreen.draw(screen)
        ChamberOfDoubts.UImanager.update()
        # ChamberOfDoubts.network.update()
        # ChamberOfDoubts.play()
        pygame.display.flip()



        if ChamberOfDoubts.game.gun.permission and ChamberOfDoubts.game.myInventory.permission:
            ChamberOfDoubts.game.myInventory.permission = False
        elif not ChamberOfDoubts.game.gun.permission and not ChamberOfDoubts.game.myInventory.permission:
            ChamberOfDoubts.game.gun.permission = True
            ChamberOfDoubts.game.opponentInventory.permission = True

    pygame.quit()
