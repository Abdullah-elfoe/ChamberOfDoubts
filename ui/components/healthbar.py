import pygame

class HealthBar:
    def __init__(self, pos, total_width, height, max_health, color_full=(200, 50, 50), color_empty=(60, 60, 60)):
        self.pos = pos  # (x, y) position
        self.total_width = total_width
        self.height = height
        self.max_health = max_health
        self.current_health = max_health
        self.color_full = color_full
        self.color_empty = color_empty
        self.alive = True
        self.permission = True

    def hit(self, default=1):
        if self.current_health > 0:
            self.current_health -= default

    def heal(self):
        if self.current_health < self.max_health:
            self.current_health += 1
        return self

    def draw(self, surface):
        # print(self.permission)
        if not self.permission:
            return 
        x, y = self.pos
        padding = 2  # Space between squares

        # Calculate size of each square based on total width and number of health points
        square_width = (self.total_width - (self.max_health - 1) * padding) / self.max_health
        self.safetyCheck()
        for i in range(self.max_health):
            rect = pygame.Rect(
                x + i * (square_width + padding),
                y,
                square_width,
                self.height
            )
            color = self.color_full if i < self.current_health else self.color_empty
            pygame.draw.rect(surface, color, rect, border_radius=3)

    def safetyCheck(self):
        if self.current_health <= 0:
            self.alive = False

def main():
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Diamond Panel with Diamond Mini Buttons")

    clock = pygame.time.Clock()

    
    # Create a health bar with 10 squares, 300px wide, 20px tall
    health_bar = HealthBar(pos=(50, 50), total_width=300, height=20, max_health=4)
    health_bar.hit()
    health_bar.hit()
    health_bar.heal()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        screen.fill((30, 30, 30))  # Background
        health_bar.draw(screen)
        pygame.display.flip()
        clock.tick(60)


    pygame.quit()

if __name__ == "__main__":
    main()
