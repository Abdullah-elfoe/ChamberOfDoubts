""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../../')))
""" Reseting the root diretory manually"""

import pygame
from config.sounds import FIRE, MISSSHOT


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
        self.frames = [pygame.transform.scale(frame, (int(frame.get_size()[0] * 1.4), int(frame.get_size()[1] * 1.4))) for frame in self.frames]
        super().__init__(self.frames,pos,  frame_duration=3, loop=False)
        self.permission = True
        self.fire_permission = True
        self.fired = False

    def fire(self):
        if self.permission and self.fire_permission:
            self.play()
            self.fired = True


    def toggle(self):
        if self.permission:
            self.permission = False
        elif not self.permission:
            self.permission = True
    
    def draw(self, surface):
        if self.permission:
            super().draw(surface)

    def GrantPermission(self):
        self.permission = True

    def Refuse(self):
        self.permission = False

if __name__ == "__main__":

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


        gun.update()

        screen.fill((30, 30, 30))
        gun.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()