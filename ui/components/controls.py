""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""


import pygame
from config import game
from scripts.timer import Timer
pygame.init()
pygame.font.init()

class Button:
    def __init__(self, x, y, width, height, text, base_color=(0, 0, 0), hover_color=(100, 100, 100)):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.grow_factor = 1.1
        self.is_hovered = False
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.base_rect.collidepoint(mouse_pos)

        color = self.hover_color if self.is_hovered else self.base_color
        rect = self.base_rect

        # Grow when hovered
        if self.is_hovered:
            grow_width = int(self.base_rect.width * (self.grow_factor - 1) / 2)
            grow_height = int(self.base_rect.height * (self.grow_factor - 1) / 2)
            rect = pygame.Rect(
                self.base_rect.x - grow_width,
                self.base_rect.y - grow_height,
                int(self.base_rect.width * self.grow_factor),
                int(self.base_rect.height * self.grow_factor)
            )

        pygame.draw.rect(surface, color, rect, border_radius=8)

        text_surf = self.font.render(self.text, True, (0, 255, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1


class ButtonManager:
    def __init__(self):
        self.buttons = []
        self.permission = True
        self.selected = ""

    def add_button(self, button: Button):
        self.buttons.append(button)

    def draw_all(self, surface):
        for btn in self.buttons:
            if self.permission:
                btn.draw(surface)

    def handle_event(self, event, functions=[]):
        for btn in self.buttons:
            if self.permission and btn.is_clicked(event):
                print(f"Button '{btn.text}' clicked!")
                self.permission = False
                self.selected = btn.text
                for function in functions:
                    function()



class MiniButton:
    def __init__(self, name, center, size, image=None):
        self.name = name
        self.center = center
        self.size = size
        self.image = game.CONTROLS_PATH[name]
        self.image = pygame.image.load(self.image).convert_alpha()
        self.is_hovered = False

        # Simple square rect for hover detection
        half = size / 2
        self.rect = pygame.Rect(center[0] - half, center[1] - half, size, size)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def detect_click(self, mouse_pos, functions ,mouse_pressed=pygame.mouse.get_pressed()):
        """
        Detects if the button was clicked.
        :param mouse_pos: Current mouse (x, y) position.
        :param mouse_pressed: Mouse button states, e.g. pygame.mouse.get_pressed().
        :return: True if clicked, False otherwise.
        """
        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            for function in functions:
                function()
            return True

    def draw(self, surface):
        # Draw as a diamond shape (rotated square)
        half = self.size / 2
        points = [
            (self.center[0], self.center[1] - half),  # Top
            (self.center[0] + half, self.center[1]),  # Right
            (self.center[0], self.center[1] + half),  # Bottom
            (self.center[0] - half, self.center[1])   # Left
        ]

        # Choose color based on hover
        color = (200, 200, 50) if self.is_hovered else (150, 150, 150)
        pygame.draw.polygon(surface, color, points)

        # Draw image (if any)
        if self.image is not None:
            image_width = self.image.get_width()
            image_height = self.image.get_height()
            image_x = self.center[0] - image_width / 2
            image_y = self.center[1] - image_height / 2
            surface.blit(self.image, (image_x, image_y))


class DiamondPanel:
    def __init__(self, center, size, button_size_ratio=0.25, button_offset_ratio=0.35):
        self.center = center
        self.size = size

        self.color = (100, 100, 100)
        self.timer = Timer(0, 40)
        self.pressed = False

        # Define main diamond points
        half = size / 2
        self.points = [
            (center[0], center[1] - half),  # Top
            (center[0] + half, center[1]),  # Rightpygame.mixer.init()

            (center[0], center[1] + half),  # Bottom
            (center[0] - half, center[1])   # Left
        ]

        # Create 4 MiniButtons in diamond arrangement
        btn_size = size * button_size_ratio
        offset = size * button_offset_ratio

        self.buttons = [
            MiniButton("Shoot", (center[0], center[1] - offset), btn_size),  # Top
            MiniButton("Inventory",(center[0] + offset, center[1]), btn_size),  # Right
            MiniButton("Inventory",(center[0], center[1] + offset), btn_size),  # Bottom
            MiniButton("Inventory",(center[0] - offset, center[1]), btn_size),  # Left

        ]



    def draw(self, surface, mouse_pos, functions:dict={}):
        # Draw main diamond
        pygame.draw.polygon(surface, self.color, self.points)

        # Draw mini buttons
        for btn in self.buttons:
            btn.draw(surface)
            btn.check_hover(mouse_pos)
            
            if self.pressed:
                self.timer.start
            if self.timer.finished:
                self.pressed = False
            if not self.pressed:
                self.pressed = btn.detect_click(mouse_pos, functions.get(btn.name,[]), pygame.mouse.get_pressed())


def main():
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Diamond Panel with Diamond Mini Buttons")

    clock = pygame.time.Clock()

    # Create a diamond panel with size and button controls
    diamond = DiamondPanel(
        center=(400, 300),
        size=150,                # Size of the diamond panel
        button_size_ratio=0.5,   # Size of mini-buttons relative to the panel
        button_offset_ratio=0.3  # Distance of mini-buttons from center
    )
    manager = ButtonManager()
    # Optional: Load images into buttons
    # icon = pygame.image.ontrolload("icon.png").convert_alpha()
    # for btn in diamond.buttons:
    #     btn.image = iconOptions

    manager.add_button(Button(300, 200, 200, 60, "Self"))
    manager.add_button(Button(300, 300, 200, 60, "Opponent"))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.handle_event(event)

        mouse_pos = pygame.mouse.get_pos()

        screen.fill((30, 30, 30))  # Background
        diamond.draw(screen, mouse_pos)
        manager.draw_all(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
