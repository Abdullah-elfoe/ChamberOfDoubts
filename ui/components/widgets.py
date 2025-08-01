# widgets.py
import pygame
import time
from .controls import LabelButton


class Label:
    def __init__(self, text, pos, size=20, color=(255, 255, 255), font_name=None):
        self.text = text
        self.pos = pos
        self.size = size
        self.color = color
        self.font = pygame.font.SysFont(font_name, self.size)
        self.rendered = self.font.render(self.text, True, self.color)
        self.permission = True

    def draw(self, surface):
        if self.permission:
            surface.blit(self.rendered, self.pos)



class TextWidget:
    def __init__(self, rect, font, text_color=(0, 0, 0), bg_color=None, editable=True, max_lines=5):
        self.rect = pygame.Rect(rect)
        self.original_height = self.rect.height
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color  # None = transparent
        self.text = ''
        self.active = False
        self.editable = editable
        self.line_spacing = 5

        # Cursor properties
        self.cursor_visible = True
        self.last_blink = time.time()
        self.blink_interval = 0.5  # seconds
        self.permission = True
        self.max_lines = max_lines
        # NOTE TO USER: Your TextWidget currently does NOT have a max_lines parameter or logic.
        # To truly enforce a max line limit for the TextWidget, you would need to add
        # 'self.max_lines = max_lines' in its __init__ and modify its handle_event
        # to check 'len(self.wrap_text(prospective_text, self.rect.width)) <= self.max_lines'
        # before adding new characters or newlines.
        # For now, Notebook will *pass* a max_lines argument, but TextWidget will ignore it
        # unless you modify TextWidget itself.

    def handle_event(self, event):
        if not self.editable or not self.permission:
            # print(not self.editable, self.permission) # Removed print for cleaner output
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.text += '\n'
            else:
                self.text += event.unicode

    def wrap_text(self, text, max_width):
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split(' ')
            line = ""
            for word in words:
                test_line = (line + ' ' + word).strip()
                if self.font.size(test_line)[0] <= max_width - 10:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        return lines

    def update_cursor(self):
        # Blink the cursor
        if time.time() - self.last_blink > self.blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_blink = time.time()

    def draw(self, surface):
        if not self.permission:
            return
        lines = self.wrap_text(self.text, self.rect.width)
        total_height = len(lines) * (self.font.get_height() + self.line_spacing) + 10
        self.rect.height = max(self.original_height, total_height) # This makes TextWidget itself auto-adjust its height

        if self.bg_color is not None:
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            s.fill(self.bg_color)
            surface.blit(s, self.rect.topleft)

        y_offset = self.rect.y + 5
        for i, line in enumerate(lines):
            rendered = self.font.render(line, True, self.text_color)
            surface.blit(rendered, (self.rect.x + 5, y_offset))
            y_offset += self.font.get_height() + self.line_spacing

        # Draw blinking cursor (if active & editable)
        if self.active and self.editable:
            self.update_cursor()
            if self.cursor_visible:
                if lines:
                    last_line = lines[-1]
                    cursor_x = self.rect.x + 5 + self.font.size(last_line)[0]
                    cursor_y = self.rect.y + 5 + (len(lines)-1) * (self.font.get_height() + self.line_spacing)
                else:
                    cursor_x = self.rect.x + 5
                    cursor_y = self.rect.y + 5

                cursor_height = self.font.get_height()
                pygame.draw.line(surface, self.text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

class MessageBubble:
    def __init__(self, x, y, width, head, message, font):
        self.rect = pygame.Rect(x, y, width, 60)
        self.head = head
        self.message = message
        self.font = font
        self.icon_color = (0, 200, 200)
        self.lines = self.wrap_text(message, width - 50)
        self.line_height = font.get_height()
        self.rect.height = 10 + self.line_height * len(self.lines) + 20  # dynamic height

    def wrap_text(self, text, max_width):
        if text is None:
            text = "EMPTY MESSAGE"
        words = text.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if self.font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def draw(self, surface, offset_y=0):
        if self.lines is None:
            self.lines = 2
        rect = self.rect.move(0, offset_y)
        pygame.draw.rect(surface, (240, 240, 240), rect, border_radius=6)
        pygame.draw.circle(surface, self.icon_color, (rect.x + 15, rect.y + 15), 10)

        head_surf = self.font.render(self.head, True, (0, 0, 0))
        surface.blit(head_surf, (rect.x + 35, rect.y + 5))

        for i, line in enumerate(self.lines):
            msg_surf = self.font.render(line, True, (50, 50, 50))
            surface.blit(msg_surf, (rect.x + 35, rect.y + 25 + i * self.line_height))


class Notebook:
    def __init__(self, pos, tabs, font):
        self.tabs = tabs
        self.current_tab = 0
        self.font = font
        self.tab_height = 30
        self.tab_width = 100
        self.pos = pygame.Vector2(pos[0],pos[1])
        self.drag_offset = pygame.Vector2(0, 0)
        self.dragging = False
        self.width = 400
        self.original_height = 300 # Store the base height of the notebook
        self.height = self.original_height # Current dynamic height of the notebook
        self.chatTab = None  
        self.chat_input_widget = None
        self.chat_send_button = None

        self.messages = {tab: [] for tab in self.tabs}
        self.scroll = {tab: 0 for tab in self.tabs}
        self.scroll_to_bottom = {tab: False for tab in self.tabs}
        self.permission = True
        self.chat_input_height_offset = 0 # Tracks how much the chat input widget extends beyond its original height

    def handle_event(self, event):
        if not self.permission:
            return
        # Handle dragging of the notebook
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if pygame.Rect(self.pos.x, self.pos.y, self.width, self.tab_height).collidepoint(mx, my):
                self.dragging = True
                self.drag_offset = pygame.Vector2(mx, my) - self.pos

            # Handle tab clicks
            tab_index = int((mx - self.pos.x) // self.tab_width)
            if self.pos.y <= my <= self.pos.y + self.tab_height and 0 <= tab_index < len(self.tabs):
                self.current_tab = tab_index
                self.scroll_to_bottom[self.tabs[self.current_tab]] = True  # defer scroll to bottom of new tab

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.pos = pygame.Vector2(event.pos) - self.drag_offset

        # Handle mouse wheel scrolling for messages
        elif event.type == pygame.MOUSEWHEEL:
            current_tab_name = self.tabs[self.current_tab]
            self.scroll[current_tab_name] += event.y * 20
            self.scroll[current_tab_name] = min(0, self.scroll[current_tab_name]) # Prevent scrolling above top

            max_scroll = self._get_max_scroll(current_tab_name)
            if self.scroll[current_tab_name] < -max_scroll:
                self.scroll[current_tab_name] = -max_scroll
            
            # Ensure we don't scroll past the top (should already be covered by min(0, ...))
            if self.scroll[current_tab_name] > 0:
                self.scroll[current_tab_name] = 0
        
        # Always pass event to chat widgets if they exist and we are on the chat tab
        self.handleChat(event)


    def draw(self, surface):
        if not self.permission:
            return
        
        current_tab_name = self.tabs[self.current_tab]

        # 2. Auto height adjust for notebook tab
        # Calculate dynamic notebook height based on chat input widget's height
        # This must happen before drawing elements that depend on the total height.
        if self.chatTab == current_tab_name and self.chat_input_widget:
            # The TextWidget's own draw method (which runs next) will update its rect.height.
            # We need to use its *current* potentially expanded height to adjust the Notebook.
            # The TextWidget's `draw` method is responsible for setting `self.chat_input_widget.rect.height`.
            # We access that updated height here.
            self.chat_input_height_offset = self.chat_input_widget.rect.height - self.chat_input_widget.original_height
            self.height = self.original_height + self.chat_input_height_offset
        else:
            self.chat_input_height_offset = 0 # Reset offset if not on chat tab
            self.height = self.original_height # Reset notebook height to original

        # Recalculate scroll to bottom based on new potential height
        if self.scroll_to_bottom[current_tab_name]:
            self.scroll[current_tab_name] = -self._get_max_scroll(current_tab_name)
            self.scroll_to_bottom[current_tab_name] = False

        # Draw main notebook background and border
        notebook_rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        pygame.draw.rect(surface, (230, 230, 230), notebook_rect) # Main background
        pygame.draw.rect(surface, (100, 100, 100), notebook_rect, 2) # Main border

        # Draw tabs
        for i, tab in enumerate(self.tabs):
            color = (200, 200, 200) if i == self.current_tab else (150, 150, 150)
            tab_rect = pygame.Rect(self.pos.x + i * self.tab_width, self.pos.y, self.tab_width, self.tab_height)
            pygame.draw.rect(surface, color, tab_rect)
            label = self.font.render(tab, True, (0, 0, 0))
            surface.blit(label, (tab_rect.x + 5, tab_rect.y + 5))

        # --- Draw message area ---
        # 3. Prevent latest message bubble from hiding under the text widget
        # Message area height needs to account for tabs and dynamic chat input height
        chat_input_area_reserved_height = 0 
        if self.chatTab == current_tab_name and self.chat_input_widget:
            # Space for the input widget and its associated margin (10px top, 10px bottom)
            chat_input_area_reserved_height = self.chat_input_widget.rect.height + 20 # Input height + 10px margin above + 10px margin below

        # The message area starts after tabs and ends before the chat input area
        message_area_y_start = self.pos.y + self.tab_height
        message_area_height = self.height - self.tab_height - chat_input_area_reserved_height

        # Define the clipping rectangle for the message display area
        # This ensures messages don't draw over the tabs or the chat input area
        clip_rect = pygame.Rect(
            self.pos.x + 5, # 5px padding from left notebook edge
            message_area_y_start + 5, # 5px padding from bottom of tabs
            self.width - 10, # 5px padding from left and right notebook edges
            message_area_height - 10 # 5px padding from top and bottom of message area
        )
        
        # Draw background and border for message area
        pygame.draw.rect(surface, (220, 220, 220), clip_rect.inflate(10,10)) # Draw slightly larger background
        pygame.draw.rect(surface, (150, 150, 150), clip_rect.inflate(10,10), 1) # Border for message area

        surface.set_clip(clip_rect) # Set clipping to confine message drawing

        # Position and draw MessageBubbles within the clipped area
        scroll_y = self.scroll[current_tab_name]
        y_cursor = clip_rect.y + scroll_y
        for bubble in self.messages[current_tab_name]:
            bubble.rect.x = clip_rect.x + 5 # 5px internal padding for bubble from clip_rect left
            bubble.rect.y = y_cursor
            bubble.draw(surface) # MessageBubble's draw uses its own self.rect.x, self.rect.y
            y_cursor += bubble.rect.height + 10 # 10px spacing between bubbles
        
        surface.set_clip(None) # Remove clipping after drawing messages

        # --- Draw chat input and send button ---
        # Only draw chat widgets if on the active chat tab
        if self.chatTab == current_tab_name:
            self.drawChat(surface)
  
    def drawChat(self, surface):
        current_tab_name = self.tabs[self.current_tab]
        if self.permission and self.chatTab == current_tab_name and self.chat_input_widget and self.chat_send_button:
            # Calculate current positions based on notebook position and its dynamically adjusted height
            # Input widget should be positioned relative to the bottom of the *current* notebook height
            input_y_pos = self.pos.y + self.height - self.chat_input_widget.rect.height - 10 # 10px from bottom of notebook

            input_rect = pygame.Rect(
                self.pos.x + 10, input_y_pos,
                self.width - 100, self.chat_input_widget.rect.height # Use TextWidget's current height for its rect
            )
            send_rect = pygame.Rect(
                self.pos.x + self.width - 80, input_y_pos, # Same Y as input
                70, 30 # Use default size as per LabelButton's default_size
            )

            # Update input widget rect and position for drawing
            self.chat_input_widget.rect.topleft = input_rect.topleft
            self.chat_input_widget.rect.width = input_rect.width # Ensure width is consistent, height handled by TextWidget draw

            # Update send button rect and position for drawing
            self.chat_send_button.rect.topleft = send_rect.topleft
            # self.chat_send_button.original_position = send_rect.topleft # Not strictly needed if topleft is set directly

            # Draw them
            self.chat_input_widget.draw(surface) # This call will cause TextWidget to update its own rect.height
            self.chat_send_button.draw(surface)
  
    def handleChat(self, event):
        # Handle text input and button click for chat tab
        if self.chatTab == self.tabs[self.current_tab]:
            if self.chat_input_widget:
                # Pass event to TextWidget for typing input
                self.chat_input_widget.handle_event(event)
            if self.chat_send_button:
                # Check for click on send button
                # Assuming LabelButton's is_clicked handles event checking and internal function calls
                if self.chat_send_button.is_clicked(event):
                    # Signal to scroll to bottom after a message is potentially sent
                    self.scroll_to_bottom[self.chatTab] = True
                    # The actual sending/processing of chat text should happen outside
                    # (e.g., in the main game loop after calling get_chat_text)

    def get_chat_text(self):
        """Returns the current text from input box and clears it."""
        if self.chat_input_widget and self.chat_input_widget.text.strip():
            text = self.chat_input_widget.text.strip()
            self.chat_input_widget.text = ""
            # Ensure the input widget's height resets after clearing text
            self.chat_input_widget.rect.height = self.chat_input_widget.original_height 
            return text
        return None
    
    def clear_chat_input(self):
        """Clears the text in the chat input box."""
        if self.chat_input_widget:
            self.chat_input_widget.text = ""
            self.chat_input_widget.rect.height = self.chat_input_widget.original_height  # Reset height if it auto-expanded

    def addToNotebook(self, tabname, head, message):
        if tabname not in self.tabs:
            print(f"Warning: Tab '{tabname}' does not exist.")
            return
        # Calculate the available width for MessageBubbles inside the message area
        # This is notebook width - (5px left clip_rect padding + 5px right clip_rect padding for the clip_rect itself)
        # - (5px internal bubble padding from clip_rect.x + 5 for bubble.rect.x) - (some buffer)
        # Let's target the inner width of the message area, which is self.width - 10 (from clip_rect)
        # Then, your MessageBubble also has a hardcoded '- 50' for icon/head
        message_area_for_bubble_width = self.width - 10 # This is the width of the clip_rect
        bubble = MessageBubble(0, 0, message_area_for_bubble_width, head, message, self.font)
        self.messages[tabname].append(bubble)
        self.scroll_to_bottom[tabname] = True  # mark for scroll during draw

    def _get_max_scroll(self, tabname):
        # Sum of heights of all bubbles + spacing between them
        content_height = sum(b.rect.height + 10 for b in self.messages[tabname]) # 10 for spacing between bubbles
        
        # Calculate visible height for messages, accounting for tabs and chat input area
        chat_input_area_reserved_height = 0
        if self.chatTab == tabname and self.chat_input_widget:
            # This is the height taken by the input widget AND the top/bottom margins around it
            chat_input_area_reserved_height = self.chat_input_widget.rect.height + 20 # 10px top margin, 10px bottom margin

        # Visible height is total notebook height minus tab height minus the chat input area.
        # Also account for the 10px internal padding of the message area clip_rect (5px top + 5px bottom)
        visible_message_area_height = self.height - self.tab_height - chat_input_area_reserved_height - 10
        
        # Max scroll should ensure the last message is visible above the chat input area
        return max(0, content_height - visible_message_area_height)
    
    def toggle(self):
        self.permission = not self.permission
        # Assuming your TextWidget and LabelButton have a toggle or equivalent method/property
        if self.chat_input_widget:
            # NOTE TO USER: Your TextWidget currently does NOT have a toggle method.
            # If you want it to also respect `self.permission`, you'd need to add one
            # or directly set `self.chat_input_widget.permission = self.permission`.
            # For now, this line will cause an AttributeError if `toggle` isn't there.
            # self.chat_input_widget.toggle()
            self.chat_input_widget.permission = self.permission
        if self.chat_send_button:
            # Assuming LabelButton has a click_enabled property or similar
            self.chat_send_button.click_enabled = self.permission 

    def setTabs(self, tabs):
        self.tabs = tabs
        self.messages = {tab: [] for tab in self.tabs}
        self.scroll = {tab: 0 for tab in self.tabs}
        self.scroll_to_bottom = {tab: False for tab in self.tabs}
   
    @property
    def chattab(self):
        return self.chatTab

    @chattab.setter
    def chattab(self, props):
        self.chatTab = props[0]
        # Initial position for chat input widget and send button.
        # Use self.original_height for initial calculation as self.height is dynamic
        input_rect = pygame.Rect(
                self.pos.x + 10, self.pos.y + self.original_height - 40, # 40px from bottom (30h input + 10 margin)
                self.width - 100, 30 # Initial fixed height for TextWidget
            )
        self.chat_input_widget = TextWidget(
                    rect=input_rect,
                    font=self.font,
                    bg_color=(255, 255, 255),
                    editable=True,
                    # 1. Set the maximum lines for the textwidget
                    # NOTE TO USER: The 'max_lines' argument is passed here,
                    # but your TextWidget class itself needs to be modified
                    # to actually use and enforce this limit in its handle_event.
                    # As provided, TextWidget will ignore this parameter.
                    # For example, you might add 'self.max_lines = max_lines' to TextWidget's __init__
                    # and then check `if len(prospective_lines) <= self.max_lines:` in `handle_event`.
                    max_lines=2 # Example: Limit to 5 lines
                )
        send_rect = pygame.Rect(
                self.pos.x + self.width - 80, self.pos.y + self.original_height - 40,
                70, 30
            )
        self.chat_send_button = LabelButton(
                    "Send", send_rect.topleft, self.font,
                    (0, 0, 0), (100, 100, 255),
                    use_default_border=True,
                    default_size=(70, 30),
                    click_enabled=True
                )
        # The `drawChat` call here is incorrect as props[1] is typically the surface,
        # but drawing should happen in the main draw loop. Removed.
        # self.drawChat(props[1]) if __name__=="__main__":
    
    def close(self):
        if self.permission:
            self.permission = False 
    
    
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Notebook Example")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)

    # Create UI elements
    title = Label("Demo Notebook UI", (10, 100), 40)
    notebook = Notebook((400, 400), ["general", "chat", "?"], font)
    text = TextWidget(pygame.Rect(0, 0, 200, 200), font, bg_color=(0, 34, 255), editable=True)




    running = True
    while running:
        screen.fill((30, 30, 30))  # background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            notebook.handle_event(event)
            # text.handle_event(event)

        # Draw widgets
        notebook.draw(screen)
        # title.draw(screen)
        # text.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()