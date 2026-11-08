"""Short sprite-sheet animations for destroyed ships."""

from pathlib import Path

import pygame


ASSET_DIR = Path(__file__).resolve().parent / "assets"


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, kind="alien"):
        super().__init__()
        filename = "player_explosion.png" if kind == "player" else "alien_explosion.png"
        sheet = pygame.image.load(str(ASSET_DIR / filename)).convert_alpha()
        frame_width = sheet.get_width() // 2
        self.frames = [
            sheet.subsurface((index * frame_width, 0, frame_width, sheet.get_height()))
            .copy()
            for index in range(2)
        ]
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)
        self.frame_duration = 100 if kind == "player" else 85
        self.frame_sequence = (0, 1, 0, 1, 1) if kind == "player" else (0, 1)
        self.started_at = pygame.time.get_ticks()

    def update(self):
        elapsed = pygame.time.get_ticks() - self.started_at
        frame_index = elapsed // self.frame_duration
        if frame_index >= len(self.frame_sequence):
            self.kill()
            return
        self.image = self.frames[self.frame_sequence[frame_index]]
