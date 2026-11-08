"""
Class for Aliens / Invaders
"""

from pathlib import Path

import pygame


ASSET_DIR = Path(__file__).resolve().parent / "assets"


class Alien(pygame.sprite.Sprite):
    def __init__(self, alien_type, x, y, column):
        super().__init__()
        self.images = [
            pygame.image.load(str(ASSET_DIR / f"Alien{alien_type}{suffix}.png"))
            .convert_alpha()
            for suffix in ("", "_2")
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.column = column
        self.frame = 0
        self.last_frame_time = pygame.time.get_ticks()

    def update(self, direction):
        self.rect.x += direction
        now = pygame.time.get_ticks()
        if now - self.last_frame_time >= 400:
            self.frame = 1 - self.frame
            self.image = self.images[self.frame]
            self.last_frame_time = now


class AlienUFO(pygame.sprite.Sprite):
    def __init__(self, spawn_from, screen_width):
        super().__init__()
        image = pygame.image.load(str(ASSET_DIR / "ship.png")).convert_alpha()
        self.image = pygame.transform.scale_by(image, 2)

        if spawn_from == "RIGHT":
            self.x = screen_width + 50
            self.speed = -2
        else:
            self.x = -50
            self.speed = 2

        self.screen_width = screen_width
        self.rect = self.image.get_rect(topleft=(self.x, 10))

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > self.screen_width:
            self.kill()