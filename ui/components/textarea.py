""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""


import pygame

import pygame

class TextBox:
    def __init__(self, x, y, width, height, title, text, font_name=None, font_size=20,
                 bg_color=(30, 30, 30), text_color=(255, 255, 255),
                 title_color=(255, 255, 255), title_bg=(50, 50, 200),
                 padding=10, border_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.text = text
        self.font = pygame.font.SysFont(font_name, font_size)
        self.title_font = pygame.font.SysFont(font_name, font_size + 2, bold=True)
        self.bg_color = bg_color
        self.text_color = text_color
        self.title_color = title_color
        self.title_bg = title_bg
        self.padding = padding
        self.border_radius = border_radius
        self.permission = True

        # For dragging
        self.dragging = False
        self.drag_offset = (0, 0)

        # Close button
        self.close_btn_size = 20
        self.close_btn_rect = pygame.Rect(
            self.rect.right - self.close_btn_size - self.padding,
            self.rect.y + self.padding // 2,
            self.close_btn_size,
            self.close_btn_size
        )

    def draw(self, surface):
        if not self.permission:
            return

        # Title bar
        title_bar_height = self.title_font.get_height() + self.padding
        title_bar_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, title_bar_height)

        # Update close button position in case box moved
        self.close_btn_rect.topleft = (
            self.rect.right - self.close_btn_size - self.padding,
            self.rect.y + self.padding // 2
        )

        # Box
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)

        # Title bar
        pygame.draw.rect(surface, self.title_bg, title_bar_rect,
                         border_top_left_radius=self.border_radius,
                         border_top_right_radius=self.border_radius)

        # Title text
        title_surf = self.title_font.render(self.title, True, self.title_color)
        surface.blit(title_surf, (self.rect.x + self.padding, self.rect.y + self.padding // 2))

        # Close button
        pygame.draw.rect(surface, (200, 50, 50), self.close_btn_rect, border_radius=5)
        x_font = self.font.render("X", True, (255, 255, 255))
        x_rect = x_font.get_rect(center=self.close_btn_rect.center)
        surface.blit(x_font, x_rect)

        # Text area
        text_area = pygame.Rect(self.rect.x + self.padding,
                                self.rect.y + title_bar_height + self.padding // 2,
                                self.rect.width - 2 * self.padding,
                                self.rect.height - title_bar_height - self.padding)
        
        lines = self.wrap_text(self.text, self.font, text_area.width)
        y = text_area.y
        for line in lines:
            line_surf = self.font.render(line, True, self.text_color)
            surface.blit(line_surf, (text_area.x, y))
            y += self.font.get_height()

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines

    def handle_event(self, event):
        if not self.permission:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.close_btn_rect.collidepoint(event.pos):
                    self.permission = False
                else:
                    title_bar_height = self.title_font.get_height() + self.padding
                    title_bar_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, title_bar_height)
                    if title_bar_rect.collidepoint(event.pos):
                        self.dragging = True
                        mouse_x, mouse_y = event.pos
                        self.drag_offset = (mouse_x - self.rect.x, mouse_y - self.rect.y)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                new_x = mouse_x - self.drag_offset[0]
                new_y = mouse_y - self.drag_offset[1]
                self.rect.topleft = (new_x, new_y)



if __name__ == "__main__":
    import sys
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TextBox Example")
    clock = pygame.time.Clock()

    # Long text to wrap
    lorem_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    )

    box = TextBox(100, 100, 600, 300, title="Notice", text=lorem_text)

    while True:
        screen.fill((20, 20, 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            box.handle_event(event)

        box.draw(screen)

        pygame.display.flip()
        clock.tick(60)
