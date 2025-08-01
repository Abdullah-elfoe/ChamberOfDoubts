""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from ui.components.widgets import TextWidget
from ui.components.controls import                                                       LabelManager
from .template import Basic
import pygame


class MiniConnectScreen(Basic):
    def __init__(self, x, y, width, height, font, function=None, parameter=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.title_bar_height = 35
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.font = font

        # Style
        self.bg_color = (30, 30, 30)
        self.title_color = (40, 40, 80)
        self.border_radius = 12
        self.input_bg = (50, 50, 60)

        # TextWidgets
        self.ip_input = TextWidget((x + 20, y + 80, width - 40, 36), font, text_color=(255, 255, 255), bg_color=self.input_bg, editable=True)
        self.port_input = TextWidget((x + 20, y + 150, width - 40, 36), font, text_color=(255, 255, 255), bg_color=self.input_bg, editable=True)

        # Connect button via LabelManager
        self.label_manager = LabelManager(font)
        self.label_manager.border_animation_enabled = True
        self.label_manager.enlarge_on_hover_enabled = True
        self.label_manager.click_enabled = True
        self.label_manager.use_default_border = True

        self.connect_label_pos = (x + (width // 2) - 60, self.rect.y + self.rect.height - 55)
        self.label_manager.add_label(
            "Connect",
            pos=self.connect_label_pos,
            color=(200, 200, 200),
            hover_color=(0, 200, 255),
            border_color=(0, 200, 255),
            use_default_border=True,
            default_size=(120, 40),
            function=function,
            parameters=parameter
        )

        # Close button
        self.close_button_rect = pygame.Rect(x + width - 35, y + 8, 25, 25)

    # def connect_action(self, _=None):
    #     ip = self.ip_input.text.strip()
    #     port = self.port_input.text.strip()
    #     self.
    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_button_rect.collidepoint(event.pos):
                self.visible = False
            elif pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.title_bar_height).collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                self.offset_x = self.rect.x - mouse_x
                self.offset_y = self.rect.y - mouse_y


        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset_x
                self.rect.y = mouse_y + self.offset_y
                self.update_positions()

        self.ip_input.handle_event(event)
        self.port_input.handle_event(event)
        self.label_manager.handle_clicks(event)

    def update(self, dt):
        if not self.visible:
            return
        self.label_manager.update(pygame.mouse.get_pos(), dt)

    def update_positions(self):
        self.ip_input.rect.topleft = (self.rect.x + 20, self.rect.y + 80)
        self.port_input.rect.topleft = (self.rect.x + 20, self.rect.y + 150)
        self.label_manager.labels[0].position = (self.rect.x + (self.rect.width // 2) - 60, self.rect.y + self.rect.height - 55)
        self.label_manager.labels[0].original_position = self.label_manager.labels[0].position
        self.label_manager.labels[0]._render()
        self.close_button_rect.topleft = (self.rect.x + self.rect.width - 35, self.rect.y + 8)

    def draw(self, surface):
        if not self.visible:
            return

        # pygame.draw.rect(surface, (255, 255,255), self.rect)
        # Background
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.title_color, (self.rect.x, self.rect.y, self.rect.width, self.title_bar_height), border_top_left_radius=12, border_top_right_radius=12)

        # Title
        title_text = self.font.render("Connect to Server", True, (255, 255, 255))
        surface.blit(title_text, (self.rect.x + 10, self.rect.y + 6))

        # Close button
        pygame.draw.rect(surface, (150, 0, 0), self.close_button_rect, border_radius=10)
        x_text = self.font.render("X", True, (255, 255, 255))
        x_rect = x_text.get_rect(center=self.close_button_rect.center)
        surface.blit(x_text, x_rect)

        # Labels
        surface.blit(self.font.render("IP Address", True, (180, 180, 180)), (self.rect.x + 20, self.rect.y + 60))
        surface.blit(self.font.render("Port", True, (180, 180, 180)), (self.rect.x + 20, self.rect.y + 130))

        # Draw inputs and connect button
        self.ip_input.permission = True
        self.port_input.permission = True
        self.ip_input.draw(surface)
        self.port_input.draw(surface)
        self.label_manager.draw(surface)

    @property
    def ipAdress(self):
        return self.ip_input.text
    
    @property
    def port(self):
        return self.port_input.text


if __name__ =="__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont(None, 28)

    mini_screen = MiniConnectScreen(200, 150, 300, 270, font)

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            mini_screen.handle_event(event)

        mini_screen.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
