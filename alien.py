"""
Class for Aliens / Invaders
"""

import pygame

class Alien(pygame.sprite.Sprite):
    def __init__(self, alien_type, alien_alt, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.alien_type = alien_type
        self.alien_alt = alien_alt

        if self.alien_alt == 1:
            file_path = 'assets/Alien' + str(alien_type) + '.png'
            self.image = pygame.image.load(file_path).convert_alpha()
            self.rect = self.image.get_rect(topleft = (self.x, self.y))
        elif self.alien_alt == 2:
            file_path_alt = 'assets/Alien' + str(alien_type) + '_2.png'
            self.image = pygame.image.load(file_path_alt).convert_alpha()
            self.rect = self.image.get_rect(topleft = (self.x, self.y))


    def update(self, direction):
        self.rect.x += direction