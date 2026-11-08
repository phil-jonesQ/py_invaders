"""
Class to define the player / ship
"""

from pathlib import Path

import pygame
from projectile import Laser


ASSET_DIR = Path(__file__).resolve().parent / "assets"


class Ship(pygame.sprite.Sprite):
    def __init__(self, pos, max_width, max_height, speed, sounds=None):
        super().__init__()
        self.image = pygame.image.load(str(ASSET_DIR / "Player.png")).convert_alpha()
        self.rect = self.image.get_rect(midbottom = pos)
        self.speed = speed
        self.sounds = sounds
        self.max_width = max_width
        self.max_height = max_height
        self.ready = True
        self.laser_time = 0
        self.laser_cool_off = 600 # 600 m/s per shot
        self.lasers = pygame.sprite.Group()
        self.laser_speed = -8

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()


    def recharge(self):
        if not self.ready:
            self.current_time = pygame.time.get_ticks()
            if self.current_time - self.laser_time >= self.laser_cool_off:
                self.ready = True

    def update(self):
        self.get_input()
        self.constrain()
        self.recharge()
        self.lasers.update()
    

    def constrain(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.max_width:
            self.rect.right = self.max_width

    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center, self.max_height, self.laser_speed))
        if self.sounds is not None:
            self.sounds.play("player_shoot")
