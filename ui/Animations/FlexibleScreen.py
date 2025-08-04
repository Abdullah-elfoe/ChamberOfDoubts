""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""


import pygame
import time
from ui.components.widgets import TextWidget
from scripts.timer import Timer
from ui.components.controls import Button

class ConfirmationWindow:
    def __init__(self, rect, font, title='', message='', title_bg=(50, 50, 50), title_color=(255, 255, 255),
                 bg_color=(230, 230, 230), border_color=(0, 0, 0), border_thickness=2,
                 image=None, buttons=None, auto_hide_secs=None, tooltip=False, trigger_rect=None):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.title = title
        self.message = message
        self.title_bg = title_bg
        self.title_color = title_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.image = image  # pygame.Surface
        self.buttons = buttons or []  # List of Button instances
        self.visible = False
        self.tooltip = tooltip
        self.trigger_rect = trigger_rect
        self.permission = False
        # Title bar height
        self.title_bar_height = 40 if self.title else 0

        # Text area (uses your TextWidget)
        text_area_rect = (self.rect.x + 20 + (self.image.get_width() + 10 if self.image else 0),
                          self.rect.y + self.title_bar_height + 20,
                          self.rect.width - 40 - (self.image.get_width() + 10 if self.image else 0),
                          100)
        self.text_widget = TextWidget(text_area_rect, font, text_color=(0, 0, 0), bg_color=None, editable=False)
        self.text_widget.text = message

        # Auto-hide using Timer
        self.timer = None
        if auto_hide_secs:
            self.timer = Timer(0, int(auto_hide_secs * 60))  # assuming 60 FPS

    def handle_event(self, event):
        for button in self.buttons:
            button.is_clicked(event)

    def update(self):
        if self.tooltip and self.trigger_rect:
            self.visible = self.trigger_rect.collidepoint(pygame.mouse.get_pos())
        elif self.timer:
            self.timer.start
            if self.timer.finished:
                self.visible = False
  
    def draw(self, surface):
        if not self.visible:
            return

        # Create a transparent surface to draw the popup
        popup_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        # Background
        pygame.draw.rect(popup_surface, self.bg_color, popup_surface.get_rect())

        # Border
        if self.border_thickness > 0:
            pygame.draw.rect(popup_surface, self.border_color, popup_surface.get_rect(), self.border_thickness)

        # Title bar
        if self.title:
            title_rect = pygame.Rect(0, 0, self.rect.width, self.title_bar_height)
            pygame.draw.rect(popup_surface, self.title_bg, title_rect)
            title_surf = self.font.render(self.title, True, self.title_color)
            popup_surface.blit(title_surf, (10, (self.title_bar_height - title_surf.get_height()) // 2))

        # Image
        if self.image:
            img_pos = (20, self.title_bar_height + 20)
            popup_surface.blit(self.image, img_pos)

        # Text (redirect draw to this surface)
        self.text_widget.draw(popup_surface)

        # Buttons
        for button in self.buttons:
            button.draw(popup_surface)

        # Now blit the popup surface onto the main surface at the popup position
        surface.blit(popup_surface, self.rect.topleft)
# Make sure to define your Button, Timer, TextWidget, and ConfirmationWindow classes above this

    def display(self, msg, color=(255, 255, 255)):
        if self.timer:
            self.message = msg
            self.text_widget.text = msg
            self.visible = True
            self.text_widget.text_color = color

def handle(ref):
    ref.visible = False

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.SRCALPHA)

    pygame.display.set_caption("Confirmation Window Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # === Instance 1: Text-only, no title, no image, no buttons, transparent ===
    popup1 = ConfirmationWindow(
        rect=(100, 100, 400, 150),
        font=font,
        message="Just a simple popup message...",
        bg_color=(0, 0, 0, 0),  # Transparent background
        border_color=(0, 0, 0, 0),  # No border
        auto_hide_secs=2
    )

    # === Instance 2: Confirmation box with title and buttons ===
    ok_button = Button(260, 350, 80, 40, "OK", function=handle)
    cancel_button = Button(360, 350, 80, 40, "Cancel", function=handle)

    popup2 = ConfirmationWindow(
        rect=(200, 150, 400, 250),
        font=font,
        title="Confirm Action",
        message="Do you want to continue?",
        buttons=[ok_button, cancel_button],
        auto_hide_secs=None
    )
    for button in popup2.buttons:
        button.parameters = popup2

    # === Instance 3: Like popup2 but with an image ===
    image = pygame.Surface((60, 60))
    image.fill((200, 100, 100))

    ok_button_img = Button(260, 450, 80, 40, "OK", function=handle)
    cancel_button_img = Button(360, 450, 80, 40, "Cancel", function=handle)

    popup3 = ConfirmationWindow(
        rect=(150, 150, 500, 300),
        font=font,
        title="Delete Item",
        message="Are you sure you want to delete this file?",
        image=image,
        buttons=[ok_button_img, cancel_button_img],
        auto_hide_secs=None
    )
    for button in popup3.buttons:
        button.parameters = popup3

    rect = pygame.Rect(100, 100, 200, 60)  # Example external trigger rect
    tooltip = ConfirmationWindow(
        rect=(120, 60, 180, 80),
        font=font,
        message="Click to confirm!",
        bg_color=(240, 240, 240),
        border_color=(120, 120, 120),
        tooltip=True,
        trigger_rect=rect
)

    running = True
    while running:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            popup1.handle_event(event)
            popup2.handle_event(event)
            popup3.handle_event(event)

        popup1.update()
        popup2.update()
        popup3.update()
        tooltip.update()
        # popup1.draw(screen)
        # popup2.draw(screen)
        # popup3.draw(screen)
        tooltip.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()