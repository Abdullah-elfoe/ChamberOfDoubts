""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config import general, ui, game
from ui.components import controls, healthbar, inventory
import pygame

pygame.init()
pygame.font.init()

class Template:
    def __init__(self, manager):
        self.manager = manager
        self.controls = controls.DiamondPanel(
            center=(general.WINDOW_WIDTH//2, general.WINDOW_HEIGHT-general.CONTROLPANEL_SIZE//2-ui.MARGIN),
            size=general.CONTROLPANEL_SIZE,                
            button_size_ratio=general.BUTTON_TO_PANEL_RATIO,   
            button_offset_ratio=general.DISTANCE_FROM_CENTER  
        )
        self.myHealthBar = healthbar.HealthBar(
            pos=(ui.MARGIN, general.WINDOW_HEIGHT-general.HEALTHBAR_HEIGHT-ui.MARGIN), 
            total_width=general.HEALTHBAR_WIDTH, 
            height=general.HEALTHBAR_HEIGHT, 
            max_health=4
        )
        self.opponentHealthBar = healthbar.HealthBar(
            pos=(general.WINDOW_WIDTH-general.HEALTHBAR_WIDTH-ui.MARGIN, general.WINDOW_HEIGHT-general.HEALTHBAR_HEIGHT-ui.MARGIN), 
            total_width=general.HEALTHBAR_WIDTH, 
            height=general.HEALTHBAR_HEIGHT, 
            max_health=4
        )
        self.myInventory = inventory.CircularInventory(
            center=(400, 300), radius=200
        )
        self.opponentInventory = inventory.SqaureInventory(
            (general.WINDOW_WIDTH//2-(general.SQUAREINVENTORY_WIDTH//2), ui.MARGIN)
            )
        print()
        font = pygame.font.SysFont("helvetica", general.PLAYER_NAME_SIZE)
        self.myname = font.render(general.PLAYER_NAME, True, (255, 255, 255))
        self.opponentName = font.render("Opponent", True, (255, 255, 255))


    def draw(self):...








if __name__ == "__main__":
  
    screen = pygame.display.set_mode((general.WINDOW_WIDTH, general.WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    template = Template(object)
    template.myInventory.addToInventory()
    running = True
    for x in game.INVENTORY_ITEMS+game.SPECIAL_ITEMS:
        template.opponentInventory.addToInventory(x)

        template.myInventory.addToInventory(x)
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((30, 30, 30))

        # Health Bars ------------------------------
        template.myHealthBar.draw(screen)
        template.opponentHealthBar.draw(screen)
        screen.blit(template.opponentName, (ui.MARGIN, general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
        screen.blit(template.myname, (general.WINDOW_WIDTH-ui.MARGIN-template.myname.get_width(), general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
        # Health Bars ------------------------------

        # Control ----------------------------------
        template.controls.draw(screen, mouse_pos)
        # Control ----------------------------------
        
        # Opponent Inventory -----------------------
        template.opponentInventory.draw(screen)
        template.opponentInventory.update(mouse_pos)
        # Opponent Inventory ----------------------

        
        # My Inventory ----------------------
        template.myInventory.draw(screen)
        template.myInventory.update(mouse_pos)
        # My Inventory ----------------------




        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


        

    
