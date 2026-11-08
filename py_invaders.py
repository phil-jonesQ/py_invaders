"""Py Invaders, a Space Invaders-style game built with Pygame."""

from random import choice, randint

import pygame

import obstacle
from alien import Alien, AlienUFO
from explosion import Explosion
from projectile import Laser
from ship import Ship
from sound_effects import SoundEffects


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SHIP_SPEED = 6
BLACK = (0, 0, 0)
WHITE = (220, 220, 220)
YELLOW = (255, 255, 0)
CYAN = (90, 220, 255)
ALIEN_SHOT_INTERVAL = 1_500
ALIEN_SHOT_SPEED = 4
ALIEN_DESCENT = 10
PLAYER_LIVES = 3
PLAYER_RESPAWN_DELAY = 700
PLAYER_INVULNERABILITY = 2_000
ALIEN_ROWS = 5
ALIEN_ROW_SPACING = 38
LEVEL_TRANSITION_DELAY = 1_800


class Game:
    def __init__(self, screen, sounds):
        self.screen = screen
        self.sounds = sounds
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 58)
        self.overlay_font = pygame.font.Font(None, 32)
        self.reset()

    def reset(self):
        self.lives = PLAYER_LIVES
        self.score = 0
        self.level = 1
        self._reset_round()

    def _reset_round(self):
        ship = Ship(
            (WINDOW_WIDTH / 2, WINDOW_HEIGHT),
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            SHIP_SPEED,
            self.sounds,
        )
        self.ship = pygame.sprite.GroupSingle(ship)
        self.blocks = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.ufo = pygame.sprite.GroupSingle()
        self.alien_direction = 1
        self.player_dead = False
        self.death_time = None
        self.invulnerable_until = 0

        block_size = 4
        bunker_spacing = WINDOW_WIDTH / 4
        bunker_width = 40
        first_bunker_x = (WINDOW_WIDTH - (3 * bunker_spacing + bunker_width)) / 2
        offsets = [index * bunker_spacing for index in range(4)]
        for offset_x in offsets:
            for row_index, row in enumerate(obstacle.shape):
                for col_index, cell in enumerate(row):
                    if cell == "x":
                        x = first_bunker_x + col_index * block_size + offset_x
                        y = WINDOW_HEIGHT - 100 + row_index * block_size
                        self.blocks.add(obstacle.Block(block_size, YELLOW, x, y))

        self._create_aliens(rows=ALIEN_ROWS, cols=10)
        now = pygame.time.get_ticks()
        self.next_alien_shot = now + ALIEN_SHOT_INTERVAL
        self.next_ufo_spawn = now + randint(8_000, 14_000)
        self.game_over = False
        self.won = False
        self.wave_complete = False
        self.wave_complete_time = None

    def _create_aliens(self, rows, cols, x_distance=56, y_distance=ALIEN_ROW_SPACING):
        formation_width = (cols - 1) * x_distance + 24
        first_alien_x = (WINDOW_WIDTH - formation_width) / 2
        level_offset = (self.level - 1) * ALIEN_ROW_SPACING
        bottom_row_y = 80 + (rows - 1) * y_distance
        max_level_offset = (
            (WINDOW_HEIGHT - 140 - bottom_row_y) // y_distance
        ) * y_distance
        level_offset = min(level_offset, max_level_offset)
        for row in range(rows):
            alien_type = 1 if row == 0 or row > 2 else row + 1
            for column in range(cols):
                x = first_alien_x + column * x_distance
                y = row * y_distance + 80 + level_offset
                self.aliens.add(Alien(alien_type, x, y, column))

    def _move_aliens(self):
        self.aliens.update(self.alien_direction)
        if not self.aliens:
            return

        left_edge = min(alien.rect.left for alien in self.aliens)
        right_edge = max(alien.rect.right for alien in self.aliens)
        at_edge = (
            self.alien_direction > 0 and right_edge >= WINDOW_WIDTH
        ) or (self.alien_direction < 0 and left_edge <= 0)
        if at_edge:
            self.alien_direction *= -1
            for alien in self.aliens:
                alien.rect.y += ALIEN_DESCENT

    def _alien_shoot(self, now):
        if not self.aliens or now < self.next_alien_shot:
            return

        bottommost_by_column = {}
        for alien in self.aliens:
            current = bottommost_by_column.get(alien.column)
            if current is None or alien.rect.bottom > current.rect.bottom:
                bottommost_by_column[alien.column] = alien

        shooter = choice(list(bottommost_by_column.values()))
        self.alien_lasers.add(
            Laser(
                shooter.rect.midbottom,
                WINDOW_HEIGHT,
                ALIEN_SHOT_SPEED,
                image_name="alien_bullet1.png",
            )
        )
        self.sounds.play("alien_shoot")
        self.next_alien_shot = now + ALIEN_SHOT_INTERVAL

    def _spawn_ufo(self, now):
        if self.ufo or now < self.next_ufo_spawn:
            return

        self.ufo.add(AlienUFO(choice(("LEFT", "RIGHT")), WINDOW_WIDTH))
        self.next_ufo_spawn = now + randint(8_000, 14_000)

    def _kill_alien(self, alien):
        center = alien.rect.center
        alien.kill()
        self.explosions.add(Explosion(center, kind="alien"))
        self.sounds.play("alien_explosion")
        self.score += 10

    def _kill_ufo(self):
        ufo = self.ufo.sprite
        if ufo is None:
            return
        center = ufo.rect.center
        ufo.kill()
        self.explosions.add(Explosion(center, kind="alien"))
        self.sounds.play("alien_explosion")
        self.score += 100

    def _kill_player(self):
        ship = self.ship.sprite
        if ship is None:
            return
        center = ship.rect.center
        self.ship.empty()
        self.player_dead = True
        self.death_time = pygame.time.get_ticks()
        self.lives -= 1
        self.explosions.add(Explosion(center, kind="player"))
        self.sounds.play("player_explosion")

    def _collisions(self):
        ship = self.ship.sprite
        if ship is not None:
            for laser in list(ship.lasers):
                if pygame.sprite.spritecollideany(laser, self.blocks):
                    pygame.sprite.spritecollide(laser, self.blocks, True)
                    laser.kill()
                    continue

                aliens_hit = pygame.sprite.spritecollide(
                    laser, self.aliens, False
                )
                if aliens_hit:
                    self._kill_alien(aliens_hit[0])
                    laser.kill()
                    continue

                if pygame.sprite.spritecollideany(laser, self.ufo):
                    self._kill_ufo()
                    laser.kill()

        for laser in list(self.alien_lasers):
            if pygame.sprite.spritecollideany(laser, self.blocks):
                pygame.sprite.spritecollide(laser, self.blocks, True)
                laser.kill()
                continue

            if (
                ship is not None
                and pygame.time.get_ticks() >= self.invulnerable_until
                and pygame.sprite.spritecollideany(laser, self.ship)
            ):
                laser.kill()
                self._kill_player()
                ship = None
                continue

            current_ship = self.ship.sprite
            if (
                current_ship is not None
                and pygame.sprite.spritecollideany(laser, current_ship.lasers)
            ):
                laser.kill()

        for alien in self.aliens:
            pygame.sprite.spritecollide(alien, self.blocks, True)

    def update(self):
        now = pygame.time.get_ticks()
        self.explosions.update()

        if self.game_over:
            return

        if self.wave_complete:
            if (
                self.wave_complete_time is not None
                and now - self.wave_complete_time >= LEVEL_TRANSITION_DELAY
            ):
                self.level += 1
                self._reset_round()
            return

        if self.player_dead:
            if self.death_time is not None and now - self.death_time >= 700:
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.alien_lasers.empty()
                    self.ship.add(
                        Ship(
                            (WINDOW_WIDTH / 2, WINDOW_HEIGHT),
                            WINDOW_WIDTH,
                            WINDOW_HEIGHT,
                            SHIP_SPEED,
                            self.sounds,
                        )
                    )
                    self.invulnerable_until = now + PLAYER_INVULNERABILITY
                    self.player_dead = False
                    self.death_time = None
            return

        ship = self.ship.sprite
        if ship is not None:
            ship.update()
        self._move_aliens()
        self.alien_lasers.update()
        self.ufo.update()

        self._spawn_ufo(now)
        self._alien_shoot(now)
        self._collisions()

        if not self.player_dead and not self.aliens:
            self.wave_complete = True
            self.wave_complete_time = now
            self.won = True

    def draw(self):
        self.screen.fill(BLACK)
        self.blocks.draw(self.screen)
        self.aliens.draw(self.screen)
        self.alien_lasers.draw(self.screen)
        self.ufo.draw(self.screen)
        self.explosions.draw(self.screen)

        ship = self.ship.sprite
        if ship is not None:
            ship.lasers.draw(self.screen)
            if (
                pygame.time.get_ticks() >= self.invulnerable_until
                or pygame.time.get_ticks() // 120 % 2 == 0
            ):
                self.ship.draw(self.screen)

        score_text = self.font.render(f"SCORE {self.score:04}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"LIVES {self.lives}", True, WHITE)
        self.screen.blit(
            lives_text,
            lives_text.get_rect(topright=(WINDOW_WIDTH - 12, 10)),
        )
        level_text = self.font.render(f"LEVEL {self.level}", True, WHITE)
        self.screen.blit(
            level_text,
            level_text.get_rect(center=(WINDOW_WIDTH // 2, 22)),
        )

        if self.game_over or self.wave_complete:
            shade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 200))
            self.screen.blit(shade, (0, 0))

            panel = pygame.Rect(0, 0, 560, 260)
            panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            pygame.draw.rect(self.screen, (14, 22, 38), panel, border_radius=18)
            pygame.draw.rect(self.screen, CYAN, panel, width=3, border_radius=18)

            message = "LEVEL COMPLETE!" if self.wave_complete else "GAME OVER"
            title = self.large_font.render(message, True, WHITE)
            if self.wave_complete:
                score = self.overlay_font.render(
                    f"GET READY FOR LEVEL {self.level + 1}", True, WHITE
                )
                restart = self.overlay_font.render(
                    "NEXT LEVEL STARTING...", True, CYAN
                )
            else:
                score = self.overlay_font.render(
                    f"FINAL SCORE: {self.score:04}", True, WHITE
                )
                restart = self.overlay_font.render(
                    "PRESS  R  OR  ENTER  TO RESTART", True, CYAN
                )
            self.screen.blit(
                title, title.get_rect(center=(panel.centerx, panel.y + 65))
            )
            self.screen.blit(
                score, score.get_rect(center=(panel.centerx, panel.y + 125))
            )
            self.screen.blit(
                restart, restart.get_rect(center=(panel.centerx, panel.y + 180))
            )
            hint = self.font.render("ESC TO QUIT", True, (175, 190, 205))
            self.screen.blit(
                hint, hint.get_rect(center=(panel.centerx, panel.y + 220))
            )

    def handle_event(self, event):
        if self.game_over and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.reset()


def main():
    pygame.init()
    pygame.display.set_caption("py_invaders V1.0.0")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    sounds = SoundEffects()
    game = Game(screen, sounds)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            game.handle_event(event)

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
