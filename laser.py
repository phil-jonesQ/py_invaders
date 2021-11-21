"""
Class to define the laser / missiles
"""

import pygame


class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, max_height, speed):
        super().__init__()
        self.image = pygame.image.load('assets\player_bullet.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.speed = speed
        self.max_height = max_height

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.max_height:
            self.kill()


    def update(self):
        self.rect.y += self.speed
        self.destroy()
    