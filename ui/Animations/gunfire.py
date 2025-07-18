""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

import pygame


class BaiscAnimation:
    def __init__(self, frames, pos, frame_duration=5, loop=False):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.pos = pos
        self.current_frame = 0
        self.ticks = 0
        self.playing = False

        self.image = self.frames[self.current_frame]

    def play(self):
        self.playing = True
        self.current_frame = 0
        self.ticks = 0

    def stop(self):
        self.playing = False
        self.current_frame = 0
        self.ticks = 0

    def update(self):
        if not self.playing:
            self.image = self.frames[0]
            return

        self.ticks += 1
        if self.ticks >= self.frame_duration:
            self.ticks = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.playing = False
                    self.current_frame = len(self.frames) - 1  # Stay on last frame

        self.image = self.frames[self.current_frame]

    def draw(self, surface):
        surface.blit(self.image, self.pos)


class Gun(BaiscAnimation):
    def __init__(self, pos):
        self.frames = [pygame.image.load(f"assets/images/gun/gun{i}.png").convert_alpha() for i in range(1, 6)]
        super().__init__(self.frames,pos,  frame_duration=3, loop=False)
        self.permission = True

    def fire(self):
        if self.permission:
            self.play()


pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


# Create gun
gun = Gun(pos=(400, 300))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gun.fire()

    gun.update()

    screen.fill((30, 30, 30))
    gun.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()