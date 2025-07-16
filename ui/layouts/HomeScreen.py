import pygame
import pygame_gui


""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config import general, ui



class Main:
    def __init__(self, manager, width, height):
        self.manager = manager
        self.showModes(*ui.MODES)
        self.bots_buttons = []
        self.input_fields = []


    def showModes(self, *names):
        for index, name in enumerate(names):
            self.bots_button = pygame_gui.elements.UIButton(
                pygame.Rect((ui.MARGIN+(index*ui.BOTSBUTTONWIDTH), ui.MARGIN), (ui.BOTSBUTTONWIDTH, ui.BOTSBUTTONHEIGHT)),
                manager=self.manager,
                text=name,
                object_id = "#modes",
                
                )
        
    def update(self, timeDelta):
        self.manager.update(timeDelta)


    def detectModes(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            button_text = event.ui_element.text

            if button_text == ui.MODES[0]:
                self.__handleBots()
            elif button_text == ui.MODES[1]:
                self.__handleMultiplayer()

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
                   



    def __handleBots(self):
        self.__clear_ui()


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

        name_entry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((ui.MARGIN, ui.MARGIN + 100), (ui.BOTSBUTTONWIDTH*len(ui.MODES), 35)),
            manager=self.manager
        )

        ip_entry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((ui.MARGIN, ui.MARGIN + 140), (ui.BOTSBUTTONWIDTH*len(ui.MODES), 35)),
            manager=self.manager
        )
        ip_entry.set_text("127.0.0.1")

        port_entry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((ui.MARGIN, ui.MARGIN + 180), (ui.BOTSBUTTONWIDTH*len(ui.MODES), 35)),
            manager=self.manager
        )
        
        port_entry.set_text("5555")

        self.input_fields.extend([name_entry, ip_entry, port_entry])

    def __clear_ui(self):
        # Destroy previous squares or input fields when switching modes
        for square in self.bots_buttons:
            square.kill()
        self.bots_buttons.clear()

        for entry in self.input_fields:
            entry.kill()
        self.input_fields.clear()



print("Working fine")