"""
Explosion Class
"""
import pygame

class Explosion(pygame.sprite.Sprite):
     def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        #self.image = pygame.image.load('assets\alien_explosion.png').convert_alpha()
        self.image = pygame.image.load('assets\player_explosion.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = (self.x, self.y))


    