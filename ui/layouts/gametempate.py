""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config import general, ui, game
from components import controls, healthbar, inventory
import pygame

pygame.init()
pygame.font.init()

class Template:
    def __init__(self, manager):
        self.manager = manager
        self.controls = controls.DiamondPanel(
            center=(400, 300),
            size=150,                
            button_size_ratio=0.5,   
            button_offset_ratio=0.3  
        )
        self.healthBar = healthbar.HealthBar(
            pos=(50, 50), 
            total_width=300, 
            height=20, 
            max_health=4
        )
        self.myInventory = inventory.CircularInventory(
            center=(400, 300), radius=200
        )
        self.opponentInventory = inventory.SqaureInventory((50, 200))

        font = pygame.font.SysFont("helvetica", 30)
        self.myname = font.render(general.PLAYER_NAME, True, (255, 255, 255))
        self.opponentName = font.render("opponent", True, (255, 255, 255))


    def draw(self):...








if __name__ == "__main__":
  
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((30, 30, 30))
        
        pygame.display.flip()
        clock.tick(60)
        inventory.useItem("Fishing Rod")

    pygame.quit()


        

    
