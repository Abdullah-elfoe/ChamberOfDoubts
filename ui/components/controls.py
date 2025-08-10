""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""


import pygame
from config import game
from scripts.timer import Timer
from config import ui, general
pygame.init()
pygame.font.init()

class Button:
    def __init__(self, x, y, width, height, text, base_color=(0, 0, 0), hover_color=(100, 100, 100), function=None, parameters=None):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.grow_factor = 1.1
        self.is_hovered = False
        self.font = pygame.font.SysFont(None, 36)
        self.function = function
        self.parameters = parameters
        

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
        if self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.function is not None:self.function(self.parameters)
            return True
        return False 


class ButtonManager:
    def __init__(self):
        self.buttons = []
        self.permission = True
        self.selected = ""

    def add_button(self, button: Button):
        self.buttons.append(button)

    def draw_all(self, surface):
        if not self.permission:
            return 
        for btn in self.buttons:

            btn.draw(surface)

    def handle_event(self, event, functions=[]):
        for btn in self.buttons:
            if self.permission and btn.is_clicked(event):
                self.permission = False
                self.selected = btn.text
                for function in functions:
                    function()

                    
    def GrantPermission(self):
        self.permission = True



class MiniButton:
    def __init__(self, name, center, size, image=None):
        self.name = name
        self.center = center
        self.size = size
        self.image = game.CONTROLS_PATH[name]
        self.image = pygame.image.load(self.image).convert_alpha()
        self.is_hovered = False
        self.permission = True

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
        if not self.permission:
            return
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
        self.permission = True

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
            MiniButton("Messages",(center[0], center[1] + offset), btn_size),  # Bottom
            MiniButton("Inventory",(center[0] - offset, center[1]), btn_size),  # Left

        ]



    def draw(self, surface):
        if not self.permission:
            return
        # Draw main diamond
        pygame.draw.polygon(surface, self.color, self.points)

        # Draw mini buttons
        for btn in self.buttons:
            btn.draw(surface)
            
    def update(self,mouse_pos, functions:dict={}):
        for btn in self.buttons:
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


class LabelButton:
    def __init__(
    self,
    text,
    pos,
    font,
    color,
    hover_color,
    border_direction="bottom",
    border_color=(255, 255, 255),
    enlarge_scale=1.1,
    border_animation_enabled=False,
    enlarge_on_hover_enabled=False,
    click_enabled=False,
    shift_on_hover_enabled=False,
    use_default_border=False,
    default_size=None,  # (width, height)
    function=None,
    parameters=None
):
    # ... existing code ...


        self.text = text
        self.font = font
        self.base_color = color
        self.hover_color = hover_color
        self.border_color = border_color
        self.current_color = color
        self.position = pos
        self.original_position = pos  # Cache to prevent infinite shifts
        self.border_direction = border_direction
        self.border_progress = 0
        self.enlarge_scale = enlarge_scale
        self.border_animation_enabled = border_animation_enabled
        self.enlarge_on_hover_enabled = enlarge_on_hover_enabled
        self.click_enabled = click_enabled
        self.shift_on_hover_enabled = shift_on_hover_enabled
        self.is_hovered = False
        self.rect = None
        self.use_default_border = use_default_border
        self.default_size = default_size
        self.function = function
        self.parameters = parameters
        self._render()

    def _render(self):
        self.text_surface = self.font.render(self.text, True, self.current_color)
        text_rect = self.text_surface.get_rect()

        if self.use_default_border and self.default_size:
            width, height = self.default_size
            self.rect = pygame.Rect(self.position[0], self.position[1], width, height)
        else:
            self.rect = self.text_surface.get_rect(topleft=self.position)


    def update(self, mouse_pos, dt, animate_speed=200):
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
            self.current_color = self.hover_color
            if self.border_animation_enabled:
                self.border_progress = min(self.rect.width, self.border_progress + animate_speed * dt)
        else:
            self.is_hovered = False
            self.current_color = self.base_color
            self.border_progress = 0

        self._render()

    def draw(self, surface):
        draw_surface = self.font.render(self.text, True, self.current_color)
        draw_rect = draw_surface.get_rect(center=self.rect.center)

        # Check hover and enlarge
        if self.enlarge_on_hover_enabled and self.is_hovered:
            scale_w = int(draw_rect.width * self.enlarge_scale)
            scale_h = int(draw_rect.height * self.enlarge_scale)

            # Enlarge the rendered surface
            scaled_surface = pygame.transform.scale(draw_surface, (scale_w, scale_h))

            # Calculate offset to shift up and left equally
            offset_x = (scale_w - draw_rect.width) // 2
            offset_y = (scale_h - draw_rect.height) // 2

            # Create a new rect centered at the same point, but accounting for offset
            scaled_rect = scaled_surface.get_rect()
            scaled_rect.center = self.rect.center

            # Blit enlarged surface
            surface.blit(scaled_surface, scaled_rect.topleft)

            # Draw scaled border if enabled
            if self.use_default_border and self.default_size:
                border_rect = pygame.Rect(
                    self.rect.left - offset_x,
                    self.rect.top - offset_y,
                    self.rect.width * self.enlarge_scale,
                    self.rect.height * self.enlarge_scale
                )
                pygame.draw.rect(surface, self.border_color, border_rect, 2)
        else:
            # Normal draw
            surface.blit(draw_surface, draw_rect.topleft)
            if self.use_default_border and self.default_size:
                pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # Animated border (no change)
        if self.is_hovered and self.border_animation_enabled:
            if self.border_direction == 'bottom':
                pygame.draw.line(surface, self.border_color,
                                (self.rect.left, self.rect.bottom + 2),
                                (self.rect.left + self.border_progress, self.rect.bottom + 2), 2)
            elif self.border_direction == 'top':
                pygame.draw.line(surface, self.border_color,
                                (self.rect.left, self.rect.top - 2),
                                (self.rect.left + self.border_progress, self.rect.top - 2), 2)
            elif self.border_direction == 'left':
                pygame.draw.line(surface, self.border_color,
                                (self.rect.left - 2, self.rect.top),
                                (self.rect.left - 2, self.rect.top + self.border_progress), 2)
            elif self.border_direction == 'right':
                pygame.draw.line(surface, self.border_color,
                                (self.rect.right + 2, self.rect.top),
                                (self.rect.right + 2, self.rect.top + self.border_progress), 2)
            elif self.border_direction == 'all':
                pygame.draw.rect(surface, self.border_color, self.rect.inflate(4, 4), 2)



    def is_clicked(self, event):
        if self.click_enabled and event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.function is not None: 
                if self.text in ui.BOTS:
                    self.parameters.botsClicked = self.text
                
                elif self.text in ui.MODES:
                    self.parameters.botsClicked = None
                    self.parameters.modClicked = self.text
                self.function(self.parameters)
            return True 
        return False


class LabelManager:
    def __init__(self, font, direction='x', spacing=20, shift_amount=10, animate_speed=500, permission=True):
        self.font = font
        self.labels = []
        self.direction = direction
        self.spacing = spacing
        self.shift_amount = shift_amount
        self.animate_speed = animate_speed
        self.permission = permission

        # Control flags
        self.border_animation_enabled = False
        self.enlarge_on_hover_enabled = False
        self.click_enabled = False
        self.shift_on_hover_enabled = False

    def add_label(self, text, pos, color=(200, 200, 200), hover_color=(255, 100, 100),
                  border_direction='bottom', border_color=(255, 255, 255), use_default_border=False, default_size=(120, 50), function=None, parameters=None):
        label = LabelButton(
            text=text,
            pos=pos,
            font=self.font,
            color=color,
            hover_color=hover_color,
            border_direction=border_direction,
            border_color=border_color,
            border_animation_enabled=self.border_animation_enabled,
            enlarge_on_hover_enabled=self.enlarge_on_hover_enabled,
            click_enabled=self.click_enabled,
            shift_on_hover_enabled=self.shift_on_hover_enabled,
            use_default_border=use_default_border,
            default_size=default_size,
            function=function,
            parameters=parameters
        )
        self.labels.append(label)

    def update(self, mouse_pos, dt):
        if not self.permission:
            return

        hovered_index = None
        for i, label in enumerate(self.labels):
            label.update(mouse_pos, dt, self.animate_speed)
            if label.is_hovered:
                hovered_index = i

        # Shift following labels (if enabled)
        if self.shift_on_hover_enabled and hovered_index is not None:
            for j in range(len(self.labels)):
                label = self.labels[j]
                if j > hovered_index:
                    if self.direction == 'x':
                        label.position = (
                            label.original_position[0] + self.shift_amount,
                            label.original_position[1]
                        )
                    else:
                        label.position = (
                            label.original_position[0],
                            label.original_position[1] + self.shift_amount
                        )
                else:
                    label.position = label.original_position
                label._render()
        else:
            # Reset to original positions
            for label in self.labels:
                label.position = label.original_position
                label._render()

    def draw(self, surface):
        if not self.permission:
            return
        for label in self.labels:
            label.draw(surface)

    def handle_clicks(self, event):
        if not self.permission:
            return
        for label in self.labels:
            label.is_clicked(event)


    def getLabel(self, name):
        for label in self.labels:
            if label.text == name:
                return label


if __name__ == "__main__":
    main()
