import pygame

class GameEngine:
    def __init__(self):
        self.player_pos = [400, 300]

    def handle_event(self, event):
        pass  # Handle key presses or mouse here

    def update(self, time_delta):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.player_pos[1] -= 200 * time_delta
        if keys[pygame.K_s]: self.player_pos[1] += 200 * time_delta
        if keys[pygame.K_a]: self.player_pos[0] -= 200 * time_delta
        if keys[pygame.K_d]: self.player_pos[0] += 200 * time_delta

    def draw(self, window):
        pygame.draw.circle(window, (255, 0, 0), (int(self.player_pos[0]), int(self.player_pos[1])), 20)
