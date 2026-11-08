"""Projectile class for player and alien lasers."""

from pathlib import Path

import pygame


ASSET_DIR = Path(__file__).resolve().parent / "assets"


class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, max_height, speed=-8, image_name="player_bullet.png"):
        super().__init__()
        self.image = pygame.image.load(str(ASSET_DIR / image_name)).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.max_height = max_height

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.max_height:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()
