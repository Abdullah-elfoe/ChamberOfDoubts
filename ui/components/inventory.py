""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

from config import game, general, ui
import pygame
import math
from scripts.timer import Timer
from scripts.items import function_list

pygame.init()

class SquareItemContainer:
    def __init__(self, topleft, width, height, color=(100, 100, 100)):
        self.x = topleft[0]
        self.y = topleft[1]
        self.rect = pygame.Rect((self.x, self.y), (width, height))
        self.color = color
        self.hover_color = (200, 200, 50)
        self.is_hovered = False
        self.holdingItem = None

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def detect_click(self, mouse_pos, mouse_pressed):
        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            return True
        return False

    def draw(self, surface):

        # Choose color based on hover state
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw the slot
        pygame.draw.rect(surface, color, self.rect, border_radius=10, width=2)
        
        # Draw the item if present
        if self.holdingItem is not None:
            item_image = self.holdingItem.image
            image_width = item_image.get_width()
            image_height = item_image.get_height()
            
            # Center the image in the slot
            imageX = self.rect.x + (self.rect.width - image_width) / 2
            imageY = self.rect.y + (self.rect.height - image_height) / 2
            
            surface.blit(item_image, (imageX, imageY))
            
            # Draw quantity text (bottom right corner, or inside a small circle)
            font = pygame.font.SysFont("helvetica", 14)
            text = font.render(str(self.holdingItem.qty), True, (255, 255, 255))
            text_rect = text.get_rect(bottomright=(self.rect.right - 4, self.rect.bottom - 4))
            
            # Optional: draw a small circle behind the text for better visibility
            circle_center = (self.rect.right - 8, self.rect.bottom - 12)
            pygame.draw.circle(surface, (0, 0, 0), circle_center, 10)
            
            surface.blit(text, text_rect)

    @property
    def isEmpty(self):
        return self.holdingItem is None


class CircularItemContainer:
    def __init__(self, center, radius, start_angle_deg, end_angle_deg, color=(100, 100, 100)):
        self.center = center
        self.radius = radius
        self.start_angle_deg = start_angle_deg
        self.end_angle_deg = end_angle_deg
        self.color = color
        self.hover_color = (200, 200, 50)
        self.is_hovered = False
        self.holdingItem = None

        # Optional: Item placeholder
        self.item = None  # Could be an image or name
        self.x1 = 0
        self.y1 = 0

    def check_hover(self, mouse_pos):
        dx = mouse_pos[0] - self.center[0]
        dy = mouse_pos[1] - self.center[1]
        distance = math.hypot(dx, dy)

        if distance > self.radius:
            self.is_hovered = False
            return

        angle = math.degrees(math.atan2(-dy, dx)) % 360

        # Handle wrap-around (e.g., from 350 to 10 degrees)
        if self.start_angle_deg < self.end_angle_deg:
            self.is_hovered = self.start_angle_deg <= angle < self.end_angle_deg
        else:
            # Wrap-around case
            self.is_hovered = angle >= self.start_angle_deg or angle < self.end_angle_deg


    def detect_click(self, mouse_pos, functions=[], mouse_pressed=pygame.mouse.get_pressed()):
        
        """
        Detects a click using existing check_hover logic and mouse button state.
        
        :param mouse_pos: (x, y) mouse position.
        :param mouse_pressed: result of pygame.mouse.get_pressed()
        :return: True if hovered and left button clicked, else False.
        """
        self.check_hover(mouse_pos)
        if self.is_hovered and mouse_pressed[0]:
            for function in functions:
                function()
            return True
        
    def draw(self, surface):
        start_rad = math.radians(self.start_angle_deg)
        end_rad = math.radians(self.end_angle_deg)

        points = [self.center]
        for angle in [start_rad, end_rad]:
            x = self.center[0] + self.radius * math.cos(angle)
            y = self.center[1] - self.radius * math.sin(angle)
            points.append((x, y))

      
        color = self.hover_color if self.is_hovered  else self.color
        pygame.draw.polygon(surface, color, points)
        self.imageX = self.center[0] + (self.radius * 0.7) * math.cos((start_rad + end_rad) / 2)
        self.imageY = self.center[1] - (self.radius * 0.7) * math.sin((start_rad + end_rad) / 2)

        self.textX = self.center[0] + (self.radius * 0.4) * math.cos((start_rad + end_rad) / 2)
        self.textY = self.center[1] - (self.radius * 0.4) * math.sin((start_rad + end_rad) / 2)

        
      
        # Optional: Draw item representation (placeholder)
        if self.holdingItem is not None:
            self.imageX-=(self.holdingItem.image.get_width()/2)
            self.imageY-=(self.holdingItem.image.get_height()/2)
            font = pygame.font.SysFont("helvetica", 14)
            text = font.render(str(self.holdingItem.qty), False, (255, 255, 255))
            text_rect = text.get_rect(center=(
                self.textX, self.textY
            ))
            pygame.draw.circle(surface, (0, 0, 0), (self.textX, self.textY), 13)
            surface.blit(text, text_rect)
            # pygame.draw.rect(surface, (255, 255, 255), (self.imageX, self.imageY, self.holdingItem.image.get_width(), self.holdingItem.image.get_height()))
            surface.blit(self.holdingItem.image, (self.imageX, self.imageY))

            # print(self.holdingItem.image.get_width())

    @property
    def isEmpty(self):
        if self.holdingItem is None:
            return True
        else:
            return False
    


class Item:
    def __init__(self, name):
        self.name = name
        self.image = pygame.image.load(game.PATHS[name]).convert_alpha() 
        self.qty = 0
        self.function = lambda: ...
        self.parameter = ...
    
    def use(self):
        self.function(self.parameter)


    

class Inventory:
    def __init__(self):
        self.inventory = []
        self.timer = Timer(0, 30)



    def addToInventory(self, name, qty=1):
        print("1")
        for container in self.inventory:
            if (container.holdingItem is not None) and (container.holdingItem.name == name):
                container.holdingItem.qty += qty
                return
        print("2")
        # print(self.inventory)
        for container in self.inventory:
            if (container.holdingItem is None):
                container.holdingItem = Item(name)
                container.holdingItem.qty = qty
                container.holdingItem.function = function_list.get(name, [None])[0]
                container.holdingItem.parameter = function_list.get(name, [None,None])[1]
                return
        print("3")
            

                     

    def useItem(self, item_name, discard=False):
        if not self.itemExists(item_name):
            return False
        for container in self.inventory:
            if container.holdingItem == None:
                continue
            elif container.holdingItem.name == item_name:
                container.holdingItem.qty -= 1
                if not discard:
                    container.holdingItem.use()
                self.streamline(container)

              
                return True
        return False

    def qtyOf(self, item_name):
        for container in self.inventory:
            if container.holdingItem == None:
                continue
            elif container.holdingItem.name == item_name:
                return container.holdingItem.qty
            
    def streamline(self, container):
        if self.qtyOf(container.holdingItem.name) == 0:
            container.holdingItem = None

    def itemExists(self, item_name):
        array = [container.holdingItem for container in self.inventory]
        for item in array[:]:
            if item is None:
                array.remove(item)
        for index, item in enumerate(array[:]):
            array[index] = item.name

        if item_name in array:
            return True
        else:
            return False
        

    def __len__(self):
        count = 0
        for container in self.inventory:
            if container.holdingItem is not None:
                count += 1
        return count
    
    def getItems(self):
        items = []
        for container in self.inventory:
            if container.holdingItem is not None:
                items.append((container.holdingItem.name, container.holdingItem.qty))
        return items
    



    
    


class SqaureInventory(Inventory):
    def __init__(self, topLeft):
        super().__init__()
        self.x, self.y = topLeft
        self.width = general.SQUAREINVENTORY_CONTAINER_WIDTH
        self.Height = general.SQUAREINVENTORY_CONTAINER_HEIGHT
        self.num_slots = game.TOTAL_ITEMS
        self.permission = True
        self.hoverPermission = False
        self.clicked = False
        self.clicked_item = ...
        self.reset = True

        for i in range(self.num_slots):
            container = SquareItemContainer((self.x, self.y), self.width, self.Height)
            self.inventory.append(container)
            self.x += (self.width + ui.MARGIN)


    def update(self, mouse_pos, mouse_pressed=None):
        self.resetHover()
        for container in self.inventory:
            if self.hoverPermission:
                self.reset = False
                container.check_hover(mouse_pos)
                if container.detect_click(mouse_pos, mouse_pressed):
                    self.clicked = True
                    if container.holdingItem is not None:
                        self.clicked_item = container.holdingItem.name

    def resetHover(self):
        if self.reset:return
        for container in self.inventory:
            container.is_hovered = False
         
         
    def toggle(self):
        if self.permission:
            self.permission = False
        elif not self.permission:
            self.permission = True

    def draw(self, surface):
        for container in self.inventory:
            if container.holdingItem is not None and self.permission:
                container.draw(surface)
    
    def GrantPermission(self):
        self.permission = True

    def Refuse(self):
        self.permission = False

    # def generateCoords(self):
    #     for container in self.inventory:
    #         if container.holdingItem is None:

    def loseItemCheck(self, inventory, ref):

        if self.hoverPermission and self.clicked:
            try:
                self.useItem(self.clicked_item, True)
                inventory.addToInventory(self.clicked_item)
                self.clicked = False
                self.clicked_item = None
                self.hoverPermission = False
                items = [(item.holdingItem.name, item.holdingItem.qty) for item in ref.opponentInventory.inventory if item.holdingItem != None]
                ref.MainRef.network.send_game({
                    "My Inventory":items
                })
                print(items, "sent")
                ref.MainRef.updateInventory()
            except:
                ...
    @property
    def isEmpty(self):
        for item in self.inventory:
            if item.holdingItem is not None:
                return False
        return True
    
    def clear(self):
        for item in self.inventory:
            item.holdingItem = None

    def resetPosition(self, pos, fullscreen):
        self.x += pos[0]
        self.shiftContainers(pos[0], fullscreen)
        ...

    def shiftContainers(self, pixels, fullscreen):
        x = general.WINDOW_WIDTH//2-(general.SQUAREINVENTORY_WIDTH//2)
        for ind, container in enumerate(self.inventory):
            ind += 1
            if fullscreen:
                print("Full Screen")
                container.rect.x  += pixels
                container.x += pixels
            else:
                print( not "Full Screen")

                container.rect.x = x
                container.x = x
                x += general.SQUAREINVENTORY_CONTAINER_WIDTH 
                x += ui.MARGIN


                
                

class CircularInventory(Inventory):

    def __init__(self, center, radius):
        super().__init__()
        self.center = center
        self.radius = radius
        self.num_slots = game.TOTAL_ITEMS
        self.slot_angle = 360 / self.num_slots
        self.permission = True
        self.used = False

        for i in range(self.num_slots):
            self.start_angle = i * self.slot_angle
            self.end_angle = (i + 1) * self.slot_angle
            container = CircularItemContainer(center, radius, self.start_angle, self.end_angle)
            container.item = f"Item {i+1}"  # Example item
            self.inventory.append(container)

    def update(self, mouse_pos, functions=[]):
        if self.permission:
            for container in self.inventory:
                if container.detect_click(mouse_pos, functions, pygame.mouse.get_pressed()) and container.holdingItem is not None and not self.used:
                    self.used = self.useItem(container.holdingItem.name)

      
        if self.used:
            self.timer.start
            if self.timer.finished:
                self.toggle(functions)
                self.used = False

    def toggle(self, f_list=[]):
        if self.permission:
            self.permission = False
        elif not self.permission:
            self.permission = True
        for f in f_list:
            f()

    def GrantPermission(self):
        self.permission = True

    def draw(self, surface):
        # print(self.permission)
        for container in self.inventory:
            if self.permission:
                container.draw(surface)

        # Draw center circle for aesthetics
        if self.permission:
            pygame.draw.circle(surface, (30, 30, 30), self.center, int(self.radius * 0.3))

    def close(self):
        if self.permission:
            self.permission = False

    @property
    def isEmpty(self):
        for item in self.inventory:
            if item.holdingItem is not None:
                return False
        return True
    
    def clear(self):
        for item in self.inventory:
            item.holdingItem = None



if __name__ == "__main__":
  

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Create inventory
    # inventory = CircularInventory(center=(400, 300), radius=200)

    inventory = SqaureInventory((30, 30))
    for item in game.SPECIAL_ITEMS+game.INVENTORY_ITEMS:
        inventory.addToInventory(item, 40)
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((30, 30, 30))
        
        inventory.draw(screen)
        inventory.update(mouse_pos)
        pygame.display.flip()
        clock.tick(60)
        inventory.useItem("Fishing Rod")

    pygame.quit()
