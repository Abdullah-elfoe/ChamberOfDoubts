""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../')))
""" Reseting the root diretory manually"""


from ui.layouts.gametemplate import Template
from config import general, ui, game, sounds
from random import choices, choice
from bots import bloom
from json import loads
from time import sleep
from scripts.timer import Timer
from scripts.items import function_list
import pygame



pygame.init()
pygame.font.init()
pygame.mixer.init()
BLOOM = bloom.Bot("Bloom")



class Game:
    def __init__(self, template):
        self.totalPhases = game.PHASES_COUNT
        self.currentPhase = 1
        self.template = template
        self.bullets = []
        self.hit = 1
        self.ExtraTurn = False
        self.gameOver = False
        self.clockUsed = False
        self.go = True
        self.timer = Timer(0, 60)
        self.configure()    

    @property
    def randomizeItems(self):
        return choices(game.INVENTORY_ITEMS+game.SPECIAL_ITEMS, k=game.PHASES[self.currentPhase][0])
    

    def initBullets(self):
        self.bullets = [choice([True, False]) for _ in range(game.PHASES[self.currentPhase][1])]

        # self.bullets = [not True for x in range(game.PHASES[self.currentPhase][1])]


    def initItems(self): 
        for item in self.randomizeItems:
            self.template.opponentInventory.addToInventory(item)

        # for item in ("Pill", "Pill"):
        for item in self.randomizeItems:
        
            self.template.myInventory.addToInventory(item)

    def initTurns(self):
        self.myTurn = choice([True, False])
        self.myTurn = True
        self.opponentTurn = True if not self.myTurn else False


    def parseData(self, data):
        ...

    def play(self):
        self.healthCheck()
        self.bulletCheck()
        self.safetyDelay()
        if not self.go:
            return


        selected = self.template.PlayerSelectionPanel.selected
        if self.myTurn:
            if selected  != "":
                self.template.gun.fire_permission = True
            if self.template.gun.fired:
                if self.bullets[0]:
                    sounds.FIRE.play()
                    self.template.myHealthBar.hit(default=self.hit) if selected.lower() == "self" else self.template.opponentHealthBar.hit(default=self.hit)
                    self.switchTurns()
                    self.ExtraTurn = False
                    self.go = False
                        
                else:
                    sounds.MISSSHOT.play()
                    if selected == "Self" and not self.ExtraTurn:
                        self.ExtraTurn = True
                    else:
                        self.switchTurns() 
                        self.ExtraTurn = False
                        self.go = False

                    

                selected = self.template.PlayerSelectionPanel.selected = ""
                self.template.gun.fire_permission = False
                self.template.gun.fired = False
                self.hit = 1
                self.template.PlayerSelectionPanel.permission = True
                self.bullets.pop(0)

            
        else:
            self.template.gun.fire_permission = False
            info = loads(BLOOM.playTurn())
            print(info)
            print(self.bullets)
            
            if self.bullets[0]:
                sounds.FIRE.play()
                self.template.opponentHealthBar.hit() if info['Selection'] == "Self" else self.template.myHealthBar.hit()
                info['turn terminated'] = True
            else:
                sounds.MISSSHOT.play()

            self.bullets.pop(0)
        
            if info['turn terminated']:
                self.switchTurns()
                self.go = False
                # sleep(0.9)

            
            # {
            #     "Selection":"self",
            #     "inventory": [(), (), ()],
            #     "health":int,
            #     "turn terminated":bool
            # }


            # bot functionality


    
    def switchTurns(self):
        if self.clockUsed:
            self.clockUsed = False
            print("USED")
            return
        if self.myTurn:
            self.opponentTurn = True
            self.myTurn = False
        else:
            self.opponentTurn = False
            self.myTurn = True
    

    def configure(self):

        self.initBullets()
        for item in game.INVENTORY_ITEMS+game.SPECIAL_ITEMS:
            function_list[item][1] = self
        

        self.initItems()
        self.initTurns()
        self.template.gun.fire_permission = False
        self.template.infoBooth.permission = False


 
    def increaseDamage(self):
        self.hit = 2

    def healthCheck(self):
        if not self.template.myHealthBar.alive:
            self.gameOver = True
            print("Opponent won")
            
        elif not self.template.opponentHealthBar.alive:
            self.gameOver = True
            print("Abdullah Won")

    def bulletCheck(self):
        if len(self.bullets) == 0:
            self.currentPhase += 1
            self.configure()
        
        
    def safetyDelay(self):
        if not self.go:
            self.timer.start
            if self.timer.finished:
                self.go = True
            
    



screen = pygame.display.set_mode((general.WINDOW_WIDTH, general.WINDOW_HEIGHT))
template = Template(object)
COD = Game(template)

def logic(template):
    
    


    template.gun.update()
    # Health Bars ------------------------------
    template.myHealthBar.draw(screen)
    template.opponentHealthBar.draw(screen)
    screen.blit(template.opponentName, (ui.MARGIN, general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
    screen.blit(template.myname, (general.WINDOW_WIDTH-ui.MARGIN-template.myname.get_width(), general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
    # Health Bars ------------------------------

    # Control ----------------------------------
    template.controls.draw(screen, mouse_pos, {"Shoot":[template.gun.fire], "Inventory":[template.myInventory.toggle, template.opponentInventory.toggle, template.gun.toggle, sounds.CLICK.play]})
    # Control ----------------------------------
    
    # Opponent Inventory -----------------------
    template.opponentInventory.draw(screen)
    template.opponentInventory.update(mouse_pos, pressed)
    template.opponentInventory.loseItemCheck(template.myInventory)
    # Opponent Inventory ----------------------

    
    # My Inventory ----------------------
    template.myInventory.draw(screen)
    template.myInventory.update(mouse_pos, [template.gun.GrantPermission, template.opponentInventory.GrantPermission, template.myInventory.toggle])
    # My Inventory ----------------------

    # Gun object-------------------------
    template.gun.draw(screen)
    # Gun object-------------------------


    # Player Selection Panel ------------
    template.PlayerSelectionPanel.draw_all(screen)
    # Player Selection Panel ------------


    template.infoBooth.draw(screen)

if __name__ == "__main__":
    
    
    
    clock = pygame.time.Clock()
    template.myInventory.toggle()
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # print(COD.bullets)
                COD.template.myHealthBar.hit()
                # COD.template.myInventory.inventory[0].holdingItem.parameter = COD.template.infoBooth
                # COD.switchTurns()
            template.PlayerSelectionPanel.handle_event(event, [sounds.CLICK.play])
            template.infoBooth.handle_event(event)


        screen.fill((30, 30, 30))
        logic(template)
        COD.play()
        # print(COD.template.opponentInventory.hoverPermission)
        if COD.gameOver:
            exit()
        







        clock.tick(40)
        pygame.display.flip()

