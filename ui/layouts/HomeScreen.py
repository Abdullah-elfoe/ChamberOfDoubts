import pygame
import pygame_gui


""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config import general, ui
# from game_engine.Networking.node import P2PNode
from scripts.Networking import P2PNetwork

pygame.font.init()
font = pygame.font.SysFont("Comic sams ms", 50)
text_surface = font.render(general.WINDOW_NAME, True, (200, 112, 9)) 



class template:
    def __init__(self, manager):
        self.uiComponentList = []
        self.terminated = False
        self.manager = manager
        self.showModes(*ui.MODES)
        self.bots_buttons = []
        self.input_fields = []
        self.connect_button = object
        self.emptyport = "5000"
        self.network = P2PNetwork(port=self.emptyPort)
        self.play = False
        # self.network.start_server(ip=self.ipAdress, port=self.emptyport)
        self.__handleBots()

                # === Main Menu Elements ===
      
        lines = [
            "The gun's weight tells you nothing only fate decides ",
            "If the next shell is your last laugh or last breath",
            "Two players. One survivor. The game isn't rigged it's just cruel"
                ]
        for i, line in enumerate(lines):
            temp = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((3+ui.MARGIN, 400+(i*ui.LINEHEIGHT)), (-1, -1)),
                text=line,
                manager=manager
                    )
            self.uiComponentList.append(temp)


        self.play_button = pygame_gui.elements.UIButton(
            pygame.Rect((ui.MARGIN, 490), (120, 50)),
            "Play",
            manager=manager,
            object_id="#custom_button"
        )


    def showModes(self, *names):
        for index, name in enumerate(names):
            self.bots_button = pygame_gui.elements.UIButton(
                pygame.Rect((ui.MARGIN+5+(index*120), ui.MARGIN), (-1, ui.BOTSBUTTONHEIGHT)),
                manager=self.manager,
                text=name,
                object_id = "#labels",                
                )
            self.uiComponentList.append(self.bots_button)
 
            
        
    def update(self, timeDelta):
        self.manager.update(timeDelta)


    def detectModes(self, event):
        if self.play:
            return
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            button_text = event.ui_element.text

            if button_text == ui.MODES[0]:
                self.__handleBots()
            elif button_text == ui.MODES[1]:
                self.__handleMultiplayer()
            if event.ui_element == self.connect_button:
                ip = self.ip_input.get_text()
                port = int(self.port_input.get_text())
                self.network.connect(ip, port)       
                self.network.send_chat("hello")

            element = event.ui_element
            if element in self.bots_buttons:
                # self.run_bot_by_name(element.text)
                self.botname = element.text
                self.play = True


        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            for index, square in enumerate(self.bots_buttons):
                if event.ui_element == square:
                    square.set_dimensions((ui.BOTSWIDTH * ui.HOVERSCALE, ui.BOTSHEIGHT * ui.HOVERSCALE))
                    square.set_text(square.text)
                    # Shift the next squares
                    for j in range(index + 1, len(self.bots_buttons)):
                        current_pos = self.bots_buttons[j].get_relative_rect().topleft
                        new_pos = (current_pos[0] + ui.SHIFT_AMOUNT, current_pos[1])
                        self.bots_buttons[j].set_relative_position(new_pos)
                        

        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            for index, square in enumerate(self.bots_buttons):
                if event.ui_element == square:
                    square.set_dimensions((ui.BOTSWIDTH, ui.BOTSHEIGHT))
                    temp = square.text
                    square.set_text("")
                    square.set_text(temp)
                    del temp

                    # Move back the next squares
                    for j in range(index + 1, len(self.bots_buttons)):
                        current_pos = self.bots_buttons[j].get_relative_rect().topleft
                        new_pos = (current_pos[0] - ui.SHIFT_AMOUNT, current_pos[1])
                        self.bots_buttons[j].set_relative_position(new_pos)


    def detectInput(self, event):
        if self.play:
            return
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            if text == "Play":
                self.handlePlay()


    def __handleBots(self):
        self.__clear_ui()
        self.network.stop_listening()

        for i,name in enumerate(ui.BOTS):
            square = pygame_gui.elements.UIButton(
                pygame.Rect((ui.MARGIN + i * (ui.BOTSWIDTH), ui.MARGIN + 100), (ui.BOTSWIDTH, ui.BOTSHEIGHT)),
                manager=self.manager,
                text=name,
                object_id="#bot_square"
            )
            self.bots_buttons.append(square)
        

            



    def __handleMultiplayer(self):
        # Remove existing UI elements first
        self.__clear_ui()

        ip_entry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((ui.MARGIN, ui.MARGIN + 100), (ui.BOTSBUTTONWIDTH*len(ui.MODES), 35)),
            manager=self.manager
        )

        port_entry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((ui.MARGIN, ui.MARGIN + 140), (ui.BOTSBUTTONWIDTH*len(ui.MODES), 35)),
            manager=self.manager
        )

        palip_entry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((ui.MARGIN, ui.MARGIN + 180), (ui.BOTSBUTTONWIDTH*len(ui.MODES), 35)),
            manager=self.manager
        )

        
        ip_entry.set_text("127.0.0.1")
        port_entry.set_text(f"{self.emptyport}")
        self.network.start_listening()

        self.input_fields.extend([ip_entry, port_entry, palip_entry])

    def __clear_ui(self):
        # Destroy previous squares or input fields when switching modes
        for square in self.bots_buttons:
            square.kill()
        self.bots_buttons.clear()

        for entry in self.input_fields:
            entry.kill()
        self.input_fields.clear()


    def handlePlay(self):
        if len(self.bots_buttons) != 0 and len(self.input_fields) == 0:
            print("Hold Tight Match making")

            self.terminate()
        else:
            # print(self.input_fields[-1].get_text())
        
            self.create_connection_popup(self.manager)
            
    @property      
    def ipAdress(self):
        import subprocess

        output = subprocess.getoutput("ipconfig")
        for line in output.splitlines():
            if "IPv4" in line:
                return line.split(":")[1].strip()
            

    @property
    def emptyPort(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))  # Bind to any free port
        port = s.getsockname()[1]
        s.close()
        return port
    
    def create_connection_popup(self, manager):
        self.popup = pygame_gui.elements.UIWindow(
            pygame.Rect((300, 200), (350, 200)),
            manager=manager,
            window_display_title="Connect to Host"  # ✅ Correct parameter
        )

        self.ip_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((20, 40), (300, 30)),
            manager=manager,
            container=self.popup
        )
        self.ip_input.set_text("127.0.0.1")

        self.port_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((20, 80), (300, 30)),
            manager=manager,
            container=self.popup
        )
        self.port_input.set_text("5000")

        self.connect_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((100, 130), (150, 40)),
            text="Connect",
            manager=manager,
            container=self.popup
        )

        return self.popup, self.ip_input, self.port_input, self.connect_button
    
    def terminate(self):
        for element in self.uiComponentList:
            element.kill()
        self.play_button.kill()
        for element in self.input_fields:
            element.kills()
        for button in self.bots_buttons:
            button.kill()
        self.uiComponentList.clear()
        self.terminated = True


            



print("Working fine")