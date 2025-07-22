""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config import general, ui, game, sounds
from ui.components import controls, healthbar, inventory
from ui.Animations import gunfire
import pygame

pygame.init()
pygame.font.init()
pygame.mixer.init()

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
            center=(general.WINDOW_WIDTH//2, general.WINDOW_HEIGHT//2), radius=general.CIRCULAR_INVENTORY_RADIUS
        )
        self.opponentInventory = inventory.SqaureInventory(
            (general.WINDOW_WIDTH//2-(general.SQUAREINVENTORY_WIDTH//2), ui.MARGIN)
            )
        
        font = pygame.font.SysFont("helvetica", general.PLAYER_NAME_SIZE)
        self.myname = font.render(general.PLAYER_NAME, True, (255, 255, 255))
        self.opponentName = font.render("Opponent", True, (255, 255, 255))


        self.gun = gunfire.Gun((general.WINDOW_WIDTH//2+70, general.WINDOW_HEIGHT//2))
        self.gun.permission = True


    def draw(self):...

pygame.mouse.get_pressed()


pygame.mixer.init()



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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for item in template.myInventory.inventory:
                        print(item.holdingItem.name)
                    template.gun.fire()

        screen.fill((30, 30, 30))
        template.gun.update()
        # Health Bars ------------------------------
        template.myHealthBar.draw(screen)
        template.opponentHealthBar.draw(screen)
        screen.blit(template.opponentName, (ui.MARGIN, general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
        screen.blit(template.myname, (general.WINDOW_WIDTH-ui.MARGIN-template.myname.get_width(), general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
        # Health Bars ------------------------------

        # Control ----------------------------------
        template.controls.draw(screen, mouse_pos, {"Shoot":[template.gun.fire, sounds.FIRE.play], "Inventory":[template.myInventory.toggle, template.opponentInventory.toggle, template.gun.toggle, sounds.CLICK.play]})
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







        clock.tick(60)
        pygame.display.flip()

    pygame.quit()


        

    
