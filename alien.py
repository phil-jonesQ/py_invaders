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


class AlienUFO(pygame.sprite.Sprite):
    def __init__(self, spawn_from, screen_width):
        super().__init__()
        self.image = pygame.image.load('assets/ship.png').convert_alpha()
        
        if spawn_from == 'RIGHT':
            self.x = screen_width + 50
            self.speed = -3
        else:
            self.x = -50
            self.speed = 3

        self.rect = self.image.get_rect(topleft = (self.x, 10))

    def update(self):
        self.rect.x += self.speed

        