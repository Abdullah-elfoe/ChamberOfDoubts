""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../')))
""" Reseting the root diretory manually"""


from ui.layouts.GameScreen import Template
from config import general, ui, game, sounds
from random import choices, choice
from bots import bloom, bot
from bots.base import PrimaryLayer
from json import loads, dumps
from time import sleep
from scripts.timer import Timer
from scripts.items import function_list
from scripts.Networking import P2PNetwork

import pygame



pygame.init()
pygame.font.init()
pygame.mixer.init()
BLOOM = bloom.Bot("Bloom")

class Base:
    def __init__(self, template):
        self.template = template
        self.network = P2PNetwork()
        self.timer = Timer(0, 60)
        self.setupMultiplayer = False
        self.setupBot = False
        self.go = True
        self.ishost = False
        self.ishostElected = False
        self.phaseshift = False
        self.inventoryUpdatedByBot = False
        self.temporaryFunctions = []

        
    @property
    def randomizeItems(self):
        return choices(game.INVENTORY_ITEMS+game.SPECIAL_ITEMS, k=game.PHASES[self.currentPhase][0])

       

class Game(Base):
    def __init__(self, template):
        super().__init__(template)
        self.totalPhases = game.PHASES_COUNT
        self.currentPhase = 1
        self.bullets = []
        self.hit = 1
        self.ExtraTurn = False
        self.gameOver = False
        self.clockUsed = False
        # self.configure()    
        
        self.myTurn = None
        self.opponentTurn = None
        
        

    
    

    def initBullets(self):
        
        self.template.myHealthBar.max_health = self.template.myHealthBar.current_health = game.PHASES[self.currentPhase][2]
        
        self.template.opponentHealthBar.max_health = self.template.opponentHealthBar.current_health = self.template.myHealthBar.max_health
        array = [choice([True, False]) for _ in range(game.PHASES[self.currentPhase][1])]
        array.insert(0, False)
        return array

        # self.bullets = [not True for x in range(game.PHASES[self.currentPhase][1])]


    def initItems(self): 
        for item in ['Glasses', 'Signal Jammer']:

        # for item in self.randomizeItems:
            self.template.opponentInventory.addToInventory(item)

        for items in ["Injection", "Pill"]:
        # for item in self.randomizeItems:
        
            self.template.myInventory.addToInventory(items)
        

        self.template.opponentInventory.addToInventory('Fishing Rod', 5)
        self.template.myInventory.addToInventory('Clock', 5)



    def initTurns(self):
        # self.myTurn = choice([True, False])
        self.myTurn = False
        self.opponentTurn = True if not self.myTurn else False


    def parseData(self, data):
        ...

    def play2(self):
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
            #     "health":int,Game
            #     "turn terminated":bool
            # }


            # bot functionality

    def playComputer(self):
        self.healthCheck()
        # self.bulletCheck()
        self.safetyDelay()
        self.initBot()
        self.checkForNewPhase()

        if not self.go:
            return

        selected = self.template.PlayerSelectionPanel.selected
        if self.myTurn:
            if selected  != "":
                self.template.gun.fire_permission = True
            else:
                if not self.template.PlayerSelectionPanel.permission:
                    self.template.PlayerSelectionPanel.GrantPermission()
                    self.phaseshift = True
            
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
                PrimaryLayer.reCalculateShells()
                self.bullets.pop(0)

            
        else:
            self.template.gun.fire_permission = False
            print(self.bullets,len(self.bullets), "pre")
            # print(self.template.opponentInventory.getItems(), "\tlogic.py computer inv top ")
            self.BOT.udpate(self.bullets, self.template.opponentHealthBar.current_health, self.template.myHealthBar.current_health, self.template.myInventory.getItems(), self.template.opponentInventory.getItems())
            choice = self.BOT.makeMove()
            self.inventoryUpdatedByBot = False


            if not self.inventoryUpdatedByBot:
                self.inventoryUpdatedByBot = True
                self.template.myInventory.clear()
                # self.template.opponentInventory.clear()
                for item, qty in self.BOT.playerItems: 
                    self.template.myInventory.addToInventory(item, qty) if qty > 0 else ...
            
            obtainedViaFishingRod = False
            # print(self.BOT.actionChain, "action chain")
            for ind, item in enumerate(self.BOT.actionChain[:]):
                if obtainedViaFishingRod:
                    obtainedViaFishingRod = False
                    self.BOT.actionChain.pop(0)
                    continue

                if item == "Fishing Rod":
                    obtainedViaFishingRod = True
                    self.template.opponentInventory.addToInventory(self.BOT.actionChain[ind+1])
                self.template.opponentInventory.useItem(item)

                sleep(2)
                self.BOT.actionChain.pop(0)

            if self.bullets[0]:
                sounds.FIRE.play()
                self.template.myHealthBar.hit(default=self.hit) if choice.lower() == "opponent" else self.template.opponentHealthBar.hit(default=self.hit)
                self.switchTurns()
                self.ExtraTurn = False
                self.go = False
                self.template.gun.fire_permission = True

                        
            else:
                sounds.MISSSHOT.play()
                if choice == "Self" and not self.ExtraTurn:
                    self.ExtraTurn = True
                    
                else:
                    self.switchTurns() 
                    self.ExtraTurn = False
                    self.go = False
                    self.template.gun.fire_permission = True
            sleep(1)
        

            
            PrimaryLayer.reCalculateShells()
            self.bullets.pop(0)
            print(self.bullets,len(self.bullets), "post")

            self.hit = 1


        
                

                


        ...

    def play(self):
        if (self.home.modClicked == "Multiplayer") and self.network.is_connected():
            self.PlayMultiplayer()
        elif self.home.botsClicked is not None:
            self.playComputer()

    def PlayMultiplayer(self):

        self.checkForNewPhase()
        if self.template.popup.visible:
            # if (self.template.popup.timer.pointer == 59) and (self.template.popup.message.lower() == "game over"):
            #     self.UImanager.showScreenNo(self.homeScreenNo)
            return
        if self.template.popup.message.lower() == "game over":
            print("Yes it is")
            self.UImanager.showScreenNo(self.homeScreenNo)
            self.gameOver = True
            return
        # My inventory init
        if not self.setupMultiplayer:
            for item in game.INVENTORY_ITEMS+game.SPECIAL_ITEMS:
                function_list[item][1] = self
            
            if not self.initMultiplayerTurns():
                return
            

            self.template.notebook.addToNotebook("General", "Game Info", f"turn :{"my" if self.myTurn else "Opponent"}")
            self.setupMultiplayer = True
            # setting paramters from None to template itself
            
            self.temporaryFunctions.append(self.template._manage)
            self.template.gun.fire_permission = False
            
       
        selected = self.template.PlayerSelectionPanel.selected
        if self.myTurn:
            if selected  != "":
                self.template.gun.fire_permission = True
            else:
                if not self.template.PlayerSelectionPanel.permission:
                    self.template.PlayerSelectionPanel.GrantPermission()
                    self.phaseshift = True
            # print(self.myTurn, self.template.gun.fired)

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
                # self.template.PlayerSelectionPanel.permission = not True
                self.bullets.pop(0)
                self.network.send_game({
                    "myTurn":self.myTurn,
                    "opponentTurn":self.opponentTurn,
                    "bullets":self.bullets,
                    "opponentHB":self.template.opponentHealthBar.current_health,
                    "myHB":self.template.myHealthBar.current_health,
                    "switched":True
                })


        else:
            # print("my turn:",self.myTurn, "\nOpponent Turn:",self.opponentTurn)
            # print(self.home.connectScreen.ipAdress)
            self.template.gun.fire_permission = False
            self.template.PlayerSelectionPanel.permission = False
            self.template.myInventory.permission = not True
    
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
        
        self.bullets = self.initBullets()
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
            # self.currentPhase += 1
            self.configure()
        
        
    def safetyDelay(self):
        if not self.go:
            self.timer.start
            if self.timer.finished:
                self.go = True
            
        # def handle_network_messages(self):
        #     for msg_type, content in self.network.update():
        #         if msg_type == "chat":
        #             chat_box.add_line(content)  # hypothetical UI widget
        #         elif msg_type == "json":
        #             game.apply_remote_move(content)  # your game logic

    
    def initMultiplayerTurns(self):
        if not self.ishostElected:
            if self.electHost():
                self.ishostElected = True
            return
        # print("pre")
        print(True if self.ishost else not True, " HOST")
        if not self.ishost:
            return True
        # print(self.ishost, "host is "+("" if self.ishostElected else "not ")+ "elected")
        # print("post")
        
        self.myTurn = choice([True, False])
        self.opponentTurn = False if self.myTurn else True
        bullets = self.initBullets()
        for item in self.randomizeItems:
            self.template.myInventory.addToInventory(item)
        for item in self.randomizeItems:
            self.template.opponentInventory.addToInventory(item)
        self.template.myInventory.addToInventory("Clock")
        self.template.myInventory.addToInventory("Glasses")
        self.template.myInventory.addToInventory("Glasses")
        self.template.myInventory.addToInventory("Switch")
        self.template.myInventory.addToInventory("Switch")

            # sending my inventory to the peer
            # for item in self.template.myInventory.inventory:
            #     print(item.holdingItem.name, self.template.myInventory.inventory)
        myItems = [(item.holdingItem.name, item.holdingItem.qty) for item in self.template.myInventory.inventory if item.holdingItem != None]
        opponentItems = [(item.holdingItem.name, item.holdingItem.qty) for item in self.template.opponentInventory.inventory if item.holdingItem != None]
        self.network.send_game({
                "myTurn":self.myTurn,
                "opponentTurn":self.opponentTurn,
                "bullets":bullets,
                "mymHB":game.PHASES[self.currentPhase][2],
                "opponentmHB":game.PHASES[self.currentPhase][2],
                "Opponent Inventory":myItems,
                "My Inventory":opponentItems
                })
        self.bullets = bullets

        return True

    def initBot(self):
        if not self.setupBot:
            self.configure()
            self.BOT = bot.Bot()
            blank, live = 0, 0
            for bullet in self.bullets:
                if bullet:
                    live += 1
                else:
                    blank += 1
            self.BOT.udpateShells(blank, live)
            self.setupBot = True
    def electHost(self):
        if self.network.peerIp is None:
            return 
        
        address = self.template.mainRef.home.connectScreen
        # print(self.network.port, address.port)
        if address.port == "":
            return
        # print(type(self.network.peerPort), "<- peer port type", type(address.port), "<- my port type")
        print(self.network.peerPort, self.network.port)
        if (self.network.peerIp < address.ipAdress) or (self.network.peerPort < self.network.port):
            self.ishost = True
        return True


    def updateInventory(self):
        items = [(item.holdingItem.name, item.holdingItem.qty) for item in self.template.myInventory.inventory if item.holdingItem != None]
        data = {
            "Opponent Inventory":items,
        }
        self.network.send_game(data)



    def checkForNewPhase(self):
        if len(self.bullets) == 0 and self.phaseshift:
            print("here in phase check")
            self.currentPhase += 1
            self.phaseshift = False
            if not self.currentPhase == 4:
                self.setupMultiplayer = False
                self.template.popup.display("level "+str(self.currentPhase))
                self.network.send_game({"phase":self.currentPhase})
            else :
                self.template.popup.display("Game Over")
                self.network.send_game({"gameOver":True})
                self.template.myInventory.inventory.clear()
                self.template.opponentInventory.inventory.clear()

    def useItem(self,item):
        self.template.opponentInventory.useItems(item)
        # match item:
        #     case "Injection":
        #         self.template.opponentHealthBar.heal()
        #     case "Clock":
        #         self.clockUsed = True
        #     case "Glasses":
        #         PrimaryLayer.isNextBlank = True if self.bullets[0] else False
        #     case "Bazuka":
        #         self.hit = 2
        #     case "Signal Jammer":
        #         self.bullets.pop(0)
        #     case "Switch":
        #         self.bullets[0] = not self.bullets[0]
        #     case "Pill":
        #         if choice([True, False]):
        #             self.template.opponentHealthBar.heal()
        #         else:
        #             self.template.opponentHealthBarlthBar.hit(1)

            
        # for container in self.template.opponent.inventory:
        #     if container.holdingItem is None: continue
        #     if container.holdingItem.name == item:
        #         container.holdingItem.qty -= 1
        #         self.template.opponentInventory.streamline(container)
        #         break

screen = pygame.display.set_mode((general.WINDOW_WIDTH, general.WINDOW_HEIGHT))
template = Template(object)
COD = Game(template)


def logic(template, mouse_pos, pressed, screen):

    
    template.gun.update()
    # Health Bars ------------------------------
    template.myHealthBar.draw(screen)
    template.opponentHealthBar.draw(screen)
    screen.blit(template.opponentName, (ui.MARGIN, general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
    screen.blit(template.myname, (general.WINDOW_WIDTH-ui.MARGIN-template.myname.get_width(), general.WINDOW_HEIGHT-(ui.MARGIN*2)-general.HEALTHBAR_HEIGHT-general.PLAYER_NAME_SIZE))
    # Health Bars ------------------------------

    # Control ----------------------------------
    template.controls.draw(screen)
 
    # Control ----------------------------------
    
    # Opponent Inventory -----------------------
    template.opponentInventory.draw(screen)
    template.opponentInventory.update(mouse_pos, pressed)
    template.opponentInventory.loseItemCheck(template.myInventory, lambda:...)
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
    
    COD.template.visible = not COD.template.visible
    moye = False
    clock = pygame.time.Clock()
    # template.myInventory.toggle()
    template.controls.permission = True
    template.myHealthBar.permission = True
    template.opponentHealthBar.permission = True
    template.gun.GrantPermission()
    template.opponentInventory.GrantPermission()
    template.PlayerSelectionPanel.permission = True
    running = True
    while running:
        update = COD.network.update()
        for msg_type, content in update:
            if msg_type == "chat":
                print(f"[Chat] {content}")
        # if not moye:
        #     moye = True
        #     COD.network.send_chat("hi from 6000")
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
        logic(template, mouse_pos, pressed, screen)
        COD.play2()
        COD.template.update(mouse_pos, None)
        # print(COD.template.opponentInventory.hoverPermission)
        if COD.gameOver:
            exit()
        







        clock.tick(40)
        pygame.display.flip()

