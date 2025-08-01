""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""


import pygame
import time
import sys
from ui.layouts.template import Basic
from ui.components.widgets import Label
from config import general


# --- MatchmakingDots Class ---
class MatchmakingDots(Basic):
    def __init__(self, center_pos, dot_radius=6, spacing=20, color=(255, 255, 255), bounce_height=10, speed=0.3):
        super().__init__()
        self.dot_radius = dot_radius
        self.spacing = spacing
        self.color = color
        self.bounce_height = bounce_height
        self.speed = speed  # seconds between dot jumps
        self.start_time = time.time()
        self.circles = 3
        self.center_x, self.center_y = center_pos
        self.title = Label("Matchmaking",(self.center_x+(self.circles*self.spacing)-20, self.center_y-self.bounce_height), 35)


    def draw(self, surface):
        if not self.visible:
            return 
        self.title.draw(surface)
        current_time = time.time() - self.start_time

        for i in range(self.circles):
            # Phase offset for bounce timing
            offset = (current_time - i * self.speed)
            bounce = abs((offset % (self.speed * 2)) - self.speed) / self.speed  # triangle wave
            dy = -bounce * self.bounce_height

            dot_x = self.center_x + (i - 1) * self.spacing
            dot_y = self.center_y + dy

            pygame.draw.circle(surface, self.color, (int(dot_x), int(dot_y)), self.dot_radius)


# --- Main Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Matchmaking Dots Animation")
    clock = pygame.time.Clock()

    # Background color and font
    bg_color = (30, 30, 30)
    font = pygame.font.SysFont(None, 36)

    # Create animation
    dots = MatchmakingDots(center_pos=(320, 240), color=(0, 200, 255))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(bg_color)

        # Optional: add label
        text = font.render("Matching Players", True, (200, 200, 200))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 180))

        # Draw animation
        dots.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
