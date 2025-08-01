""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config import general, ui, game, sounds
from ui.components import controls, healthbar, inventory, textarea, widgets
from ui.Animations import gunfire
from .template import Basic
import pygame

pygame.init()
pygame.font.init()
pygame.mixer.init()

class Template(Basic):
    def __init__(self, manager=None):
        self.mainRef = None
        super().__init__()
        # self.mainR
        self.templateName = "Game"
        self.manager = manager
        self.controls = controls.DiamondPanel(
            center=(general.WINDOW_WIDTH//2, general.WINDOW_HEIGHT-general.CONTROLPANEL_SIZE//2-ui.MARGIN),
            size=general.CONTROLPANEL_SIZE,                
            button_size_ratio=general.BUTTON_TO_PANEL_RATIO,   
            button_offset_ratio=general.DISTANCE_FROM_CENTER  
        )
        self.opponentHealthBar = healthbar.HealthBar(
            pos=(ui.MARGIN, general.WINDOW_HEIGHT-general.HEALTHBAR_HEIGHT-ui.MARGIN), 
            total_width=general.HEALTHBAR_WIDTH, 
            height=general.HEALTHBAR_HEIGHT, 
            max_health=4
        )
        self.myHealthBar = healthbar.HealthBar(
            pos=(general.WINDOW_WIDTH-general.HEALTHBAR_WIDTH-ui.MARGIN, general.WINDOW_HEIGHT-general.HEALTHBAR_HEIGHT-ui.MARGIN), 
            total_width=general.HEALTHBAR_WIDTH, 
            height=general.HEALTHBAR_HEIGHT,  
            max_health=4
        )
        self.myInventory = inventory.CircularInventory(
            center=(general.WINDOW_WIDTH//2, general.WINDOW_HEIGHT//2), radius=general.CIRCULAR_INVENTORY_RADIUS
        )
        self.opponentInventory = inventory.SqaureInventory(
            (general.WINDOW_WIDTH//2-(general.SQUAREINVENTORY_WIDTH//2), ui.MARGIN)
            )
        
        self.infoBooth = textarea.TextBox(100, 100, 150, 150, "Bullets info", "placeHolder")
        self.notebook = widgets.Notebook((300, 300), ["General"], pygame.font.SysFont(None, 24))
        
        # self.notebook.setup_chat_widgets()
        # self.infoBooth.permission = False

        self.PlayerSelectionPanel = controls.ButtonManager()
        self.PlayerSelectionPanel.add_button(controls.Button(300, 200, 200, 60, "Self"))
        self.PlayerSelectionPanel.add_button(controls.Button(300, 300, 200, 60, "Opponent"))
        

        
        font = pygame.font.SysFont("helvetica", general.PLAYER_NAME_SIZE)
        self.myname = font.render(general.PLAYER_NAME, True, (255, 255, 255))
        self.opponentName = font.render("Opponent", True, (255, 255, 255))
        self.namePermission = False


        self.gun = gunfire.Gun((general.WINDOW_WIDTH//2+70, general.WINDOW_HEIGHT//2))
        self.data = {
            "mod":None,
            "bot":None,
            "ip":None,
            "port":None
        }
        self.manage()


   

    def manage(self):
        if self.visible: 
            self.namePermission = True
            self.myHealthBar.permission = True
            self.opponentHealthBar.permission = True
            self.controls.permission = True
        else:
            self.infoBooth.permission = False
            self.gun.permission = False
            self.opponentInventory.permission = False
            self.myInventory.permission = False
            self.PlayerSelectionPanel.permission = False
            self.namePermission = False
            self.myHealthBar.permission = False
            self.opponentHealthBar.permission = False
            self.controls.permission = False
            self.notebook.permission = False

    def _manage(self):
        if not self.visible:
            return 
        self.opponentInventory.GrantPermission()
        self.gun.GrantPermission()



    def handleEvent(self, event):
        if self.PlayerSelectionPanel.permission:
            self.PlayerSelectionPanel.handle_event(event)
        if self.infoBooth.permission:
            self.infoBooth.handle_event(event)
        if self.notebook.permission:
            self.notebook.handle_event(event)

    def update(self, mouse_pos, dt):
        if not self.visible:
            return 
        self.myInventory.update(mouse_pos, [sounds.CLICK.play])
        self.opponentInventory.update(mouse_pos, pygame.mouse.get_pressed())
        self.opponentInventory.loseItemCheck(self.myInventory, self)
        self.gun.update()
        self.controls.update(mouse_pos, {
            "Shoot":[self.gun.fire], 
            "Inventory":[self.myInventory.toggle, self.opponentInventory.toggle, self.gun.toggle, sounds.CLICK.play,self.notebook.close], 
            "Messages":[sounds.CLICK.play, self.notebook.toggle, self.myInventory.close]
            }
            )



    def draw(self, surface):
        self.opponentHealthBar.draw(surface) if self.opponentHealthBar.permission else ...
        self.myHealthBar.draw(surface) if self.myHealthBar.permission else ...
        self.infoBooth.draw(surface) if self.infoBooth.permission else ...
        self.gun.draw(surface) if self.gun.permission else ...
        self.myInventory.draw(surface) if self.myInventory.permission else ...
        self.opponentInventory.draw(surface) if self.opponentInventory.permission else ...
        self.controls.draw(surface) if self.controls.permission else ...
        self.notebook.draw(surface) if self.notebook.permission else ...
        self.PlayerSelectionPanel.draw_all(surface) if self.PlayerSelectionPanel.permission else ...
        if self.namePermission:
            surface.blit(self.opponentName, (ui.MARGIN, general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
            surface.blit(self.myname, (general.WINDOW_WIDTH-ui.MARGIN-self.myname.get_width(), general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))


    def send(self,*_):
        message = self.notebook.get_chat_text()
        self.notebook.clear_chat_input()
        self.mainRef.network.send_chat(message)
        self.notebook.addToNotebook("Chats", "hey", message)

    @property
    def MainRef(self):
        return self.mainRef

    @MainRef.setter
    def MainRef(self, ref):
        self.mainRef = ref




        






pygame.mixer.init()

def game_functions():
    ...


if __name__ == "__main__":
  
    screen = pygame.display.set_mode((general.WINDOW_WIDTH, general.WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    template = Template(object)
    template.myInventory.addToInventory("Glasses")
    template.myInventory.toggle()
    running = True
    for x in game.INVENTORY_ITEMS+game.SPECIAL_ITEMS:
        template.opponentInventory.addToInventory(x)
        for y in range(23):
            template.myInventory.addToInventory(x)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        template.manage()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for item in template.myInventory.inventory:
                        print(item.holdingItem.name)
                    template.gun.fire()
            template.handleEvent(event)


        screen.fill((30, 30, 30))
        template.gun.update()

        # Health Bars ------------------------------
        template.myHealthBar.draw(screen)
        template.opponentHealthBar.draw(screen)
        screen.blit(template.opponentName, (ui.MARGIN, general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
        screen.blit(template.myname, (general.WINDOW_WIDTH-ui.MARGIN-template.myname.get_width(), general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
        # Health Bars ------------------------------

        # Control ----------------------------------
        template.controls.draw(screen)
        template.controls.update(mouse_pos, {"Shoot":[template.gun.fire, sounds.FIRE.play], "Inventory":[template.myInventory.toggle, template.opponentInventory.toggle, template.gun.toggle, sounds.CLICK.play, template.notebook.close]})
        # Control ----------------------------------
        
        # Opponent Inventory -----------------------
        template.opponentInventory.draw(screen)
        # template.opponentInventory.update(mouse_pos)
        # Opponent Inventory ----------------------

        
        # My Inventory ----------------------
        template.myInventory.draw(screen)
        template.myInventory.update(mouse_pos, [sounds.CLICK.play])
        # template.myInventory.
        # My Inventory ----------------------

        # Gun object-------------------------
        template.gun.draw(screen)
        # Gun object-------------------------


        # Player Selection Panel ------------
        # template.PlayerSelectionPanel.draw_all(screen)
        # Player Selection Panel ------------

        # Info Booth ------------
        template.infoBooth.draw(screen)
        # Info Booth ------------





        clock.tick(60)
        pygame.display.flip()

    pygame.quit()


        

    
