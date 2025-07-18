""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""


import pygame
from config import game
pygame.init()


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

        # Define main diamond points
        half = size / 2
        self.points = [
            (center[0], center[1] - half),  # Top
            (center[0] + half, center[1]),  # Right
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



    def draw(self, surface, mouse_pos):
        # Draw main diamond
        pygame.draw.polygon(surface, self.color, self.points)

        # Draw mini buttons
        for btn in self.buttons:
            btn.draw(surface)
            btn.check_hover(mouse_pos)


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

    # Optional: Load images into buttons
    # icon = pygame.image.load("icon.png").convert_alpha()
    # for btn in diamond.buttons:
    #     btn.image = icon

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_pos = pygame.mouse.get_pos()

        screen.fill((30, 30, 30))  # Background
        diamond.draw(screen, mouse_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
