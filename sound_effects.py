"""Small synthesized arcade sounds; no external audio assets are required."""

from array import array
import math
import warnings

import pygame


def _sweep(start_hz, end_hz, duration, volume=0.25):
    sample_rate = pygame.mixer.get_init()[0]
    sample_count = int(sample_rate * duration)
    samples = array("h")
    phase = 0.0
    for index in range(sample_count):
        progress = index / sample_count
        frequency = start_hz + (end_hz - start_hz) * progress
        phase += math.tau * frequency / sample_rate
        envelope = (1 - progress) ** 2
        sample = math.sin(phase) * envelope * volume
        samples.append(int(sample * 32767))
    return pygame.mixer.Sound(buffer=samples.tobytes())


class SoundEffects:
    def __init__(self):
        self.sounds = {}
        if pygame.mixer.get_init() is None:
            try:
                pygame.mixer.init(frequency=22_050, size=-16, channels=1, buffer=512)
            except pygame.error as error:
                warnings.warn(f"Audio is unavailable; continuing without sound: {error}")
                return

        self.sounds = {
            "player_shoot": _sweep(880, 300, 0.09, 0.18),
            "alien_shoot": _sweep(260, 120, 0.12, 0.14),
            "alien_explosion": _sweep(420, 90, 0.18, 0.22),
            "player_explosion": _sweep(300, 45, 0.48, 0.3),
        }

    def play(self, name):
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()
