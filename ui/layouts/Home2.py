import pygame


""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config import general, ui
# from game_engine.Networking.node import P2PNode
from scripts.Networking import P2PNetwork
from ui.components.controls import LabelManager, LabelButton, ButtonManager, Button
from scripts.items import menu_list, lobby_controls
from ui.components.widgets import TextWidget, Label
from scripts.timer import Timer
from .multiplayer import MiniConnectScreen

from .template import Basic
import pygame


class Template(Basic):
    def __init__(self):
        super().__init__()
        self.mainRef = None
        self.templateName = "Home"
        self.font = pygame.font.SysFont("Comic Sans MS", 30)
        self.gamemode = LabelManager(self.font, direction='x', spacing=30, shift_amount=20)
        self.bots = LabelManager(self.font, direction='x', spacing=30, shift_amount=20)
        self.gameName = Label("The Chamber Of Doubts", (ui.MARGIN, 300), 60, (155, 255, 155))
        self.gameDescription = TextWidget((ui.MARGIN, 350, 500, 100), self.font, (255, 255, 255))
        self.gameDescription.text = "The gun's weight tells you nothing only fate decides if the next shell is your last laugh or last breath. Two players, one survivor, the game isn't rigged it's just cruel. Better to leave now"
        self.buttonsPanel = ButtonManager()
        self.playButton = Button(ui.MARGIN, 500, 100, 60, "Play")
        self.buttonsPanel.add_button(self.playButton)
        self.buttonsPanel.add_button(Button(400, 500, 100, 60, "Leave", function=lobby_controls["Leave"][0]))
        
        self.enableRequirements()
        self.modClicked = "Computer"
        self.botsClicked = None
        self.emptyPort = "5000"
        
        self.data = {
            "mod":None,
            "bot":None,
            "ip":"127.0.0.1",
            "port":int(self.emptyPort)
        }



        for i, mod in enumerate(ui.MODES):
            self.gamemode.add_label(mod, (ui.MARGIN+(i*130), ui.MARGIN*2), function=menu_list.get("handleMod")[0], parameters=self)
            
        for i, bot in enumerate(ui.BOTS):
            self.bots.add_label(bot, (ui.MARGIN+(i*130), ui.MARGIN*5), use_default_border=True, default_size=(120,100), function=menu_list.get("handleBot")[0], parameters=self)

        # self.visible = True



    def enableRequirements(self):
        self.gamemode.border_animation_enabled = True
        self.gamemode.enlarge_on_hover_enabled = False
        self.gamemode.click_enabled = True
        self.gamemode.shift_on_hover_enabled = False

        self.bots.border_animation_enabled = False
        self.bots.enlarge_on_hover_enabled = True
        self.bots.click_enabled = True
        self.bots.shift_on_hover_enabled = True

        self.gameDescription.editable=False
        print("set")


    def manage(self):
        if self.visible:
            self.gamemode.permission = True
            self.gameDescription.permission = True
            self.gameName.permission = True
            self.buttonsPanel.permission = True

        else:
            self.bots.permission = False
            self.gamemode.permission = False
            self.bots.permission = False
            self.gameDescription.permission = False
            self.gameName.permission = False
            self.buttonsPanel.permission = False
            self.connectScreen.visible = False


    def handleEvent(self, event):
        self.buttonsPanel.handle_event(event)

        # return 
        if self.gamemode.permission:
            self.gamemode.handle_clicks(event)
            self.data["mod"] = self.modClicked
         
        if self.bots.permission:
            self.bots.handle_clicks(event)
        self.connectScreen.handle_event(event)




    def update(self, mouse_pos, dt):
        if not self.visible:
            return 
        self.gamemode.update(mouse_pos, dt)
        self.bots.update(mouse_pos, dt)
        

    def draw(self, surface):
        if self.gamemode.permission:
            self.gamemode.draw(surface)
        if self.bots.permission:
            self.bots.draw(surface)
        self.gameDescription.draw(surface)
        self.gameName.draw(surface)
        self.buttonsPanel.draw_all(surface)
        self.connectScreen.draw(surface)

    def setMainRef(self, ref):
        self.mainRef = ref
        self.playButton.function = lobby_controls["Play"][0]
        self.playButton.parameters = ref
        self.connectScreen = MiniConnectScreen(200, 150, 300, 270,self.font, function=lobby_controls["Connect"][0])
        self.connectScreen.label_manager.getLabel("Connect").parameters = self

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    template = Template()


    running = True
    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            template.handleEvent(event)
            


        template.update(mouse_pos, dt)
        screen.fill((30, 30, 30))
        template.manage()
        template.draw(screen)
        pygame.display.flip()
    pygame.quit()
