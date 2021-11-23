""" py_invaders - space invaders clone coded in python with pygame
game assets credit - Benedict Gaster
"""
import pygame, sys
from pygame import time
from random import choice, randint

from pygame.event import get
from ship import Ship
import obstacle
from alien import Alien
from alien import AlienUFO
from laser import Laser
from explosion import Explosion


"""
Define our Classes
"""
class Game:
        def __init__(self):
            # Ship / Player Setup
            ship_sprite = Ship((WINDOW_WIDTH / 2, WINDOW_HEIGHT), WINDOW_WIDTH, WINDOW_HEIGHT, SHIP_SPEED)
            self.ship = pygame.sprite.GroupSingle(ship_sprite)

            # Obstacle setup
            self.shape = obstacle.shape
            self.block_size = 4
            self.blocks = pygame.sprite.Group()
            self.obstacle_amount = 4
            self.obstacle_x_positions = [num * (WINDOW_WIDTH / self.obstacle_amount) for num in range(self.obstacle_amount)]
            self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = WINDOW_WIDTH / 15, y_start = WINDOW_HEIGHT - 60)

            # Alien setup
            self.aliens = pygame.sprite.Group()
            self.aliens_alt = pygame.sprite.Group()
            self.alien_lasers = pygame.sprite.Group()
            self.explode_alien = pygame.sprite.GroupSingle()
            self.alien_setup(rows = 7, cols = 12)
            self.alien_direction = 1

            # UFO Setup
            self.ufo = pygame.sprite.GroupSingle()
            self.ufo_spawn_time = randint(40, 80)

            # Other GameSetup
            self.start_time = 0
            self.alien_shoot_time = 0
            self.alien_shoot_window = 3
            self.flip_time = 30
            self.alien_shoot_threshold = 60
            self.start_difficulty = 6 # Lower to make the game harder
            self.difficulty = self.start_difficulty  

        def create_obstacle(self, x_start, y_start, offset_x):
            for row_index, row in enumerate(self.shape):
                for col_index, col in enumerate(row):
                    if col == 'x':
                        x = x_start + col_index * self.block_size + offset_x
                        y = y_start + row_index * self.block_size
                        block = obstacle.Block(self.block_size, YELLOW, x, y)
                        self.blocks.add(block)

        def create_multiple_obstacles(self, *offset, x_start, y_start):
            for offset_x in offset:
                self.create_obstacle(x_start, y_start, offset_x)

        def alien_setup(self, rows, cols, x_distance = 40, y_distance = 28, x_offset = 10, y_offset = 40):
            for row_index, row in enumerate(range(rows)):
                for col_index, col in enumerate(range(cols)):
                    x = col_index * x_distance + x_offset
                    y = row_index * y_distance + y_offset
                    # Alien_Type, Alien_Frame
                    if row_index == 0:
                        alien_sprite = Alien(1, 1, x, y)
                        alien_sprite_alt = Alien(1, 2, x, y)
                    elif row_index == 1:
                        alien_sprite = Alien(2, 1, x, y)
                        alien_sprite_alt = Alien(2, 2, x, y)
                    elif row_index == 2:
                        alien_sprite = Alien(3, 1, x, y)
                        alien_sprite_alt = Alien(3, 2, x, y)
                    else: 
                        alien_sprite = Alien(1, 1, x, y)
                        alien_sprite_alt = Alien(1, 2, x, y)
                    self.aliens.add(alien_sprite)
                    self.aliens_alt.add(alien_sprite_alt)

        def alien_position_checker(self):
            
            all_aliens = self.aliens.sprites()
            all_aliens_alt = self.aliens_alt.sprites()
            for alien in all_aliens:
                if alien.rect.left <= 0:
                    self.alien_direction = 1
                    self.difficulty -= 1
                    if self.difficulty < 0:
                        self.difficulty = self.start_difficulty
                        self.alien_move_down(1)
                if alien.rect.right >= WINDOW_WIDTH:
                    self.alien_direction = -1
            for alien_alt in all_aliens_alt:
                if alien_alt.rect.left <= 0:
                    self.alien_direction = 1
                    if self.difficulty < 0:
                        self.difficulty = self.start_difficulty
                        self.alien_move_down(1)
                if alien_alt.rect.right >= WINDOW_WIDTH:
                    self.alien_direction = -1
                
        def alien_move_down(self, distance):
            if self.aliens:
                for alien in self.aliens.sprites():
                    alien.rect.y += distance
            if self.aliens_alt:
                for alien_alt in self.aliens_alt.sprites():
                    alien_alt.rect.y += distance

        def alien_shoot(self):
            if self.aliens.sprites() or self.aliens_alt.sprites():
                random_alien = choice(self.aliens.sprites())
                random_alien_alt = choice(self.aliens_alt.sprites())
                laser_sprite = Laser(random_alien.rect.center, WINDOW_HEIGHT, 6)
                laser_sprite_alt = Laser(random_alien_alt.rect.center, WINDOW_HEIGHT, 6)
                self.alien_lasers.add(laser_sprite)
                self.alien_lasers.add(laser_sprite_alt)

        def ufo_timer(self):
            self.ufo_spawn_time -= 1
            if self.ufo_spawn_time <= 0:
                self.ufo.add(AlienUFO(choice(['LEFT', 'RIGHT']), WINDOW_WIDTH))
                self.ufo_spawn_time = randint(400, 800)

        def get_delay_timer(self):
            self.start_time += 1
            if self.start_time > (self.flip_time * 2):
                self.start_time = 0
            return self.start_time

        def delay_alien_fire(self):
            #print(self.alien_shoot_time)
            self.alien_shoot_time += 1
            if self.alien_shoot_time > (self.alien_shoot_threshold + self.alien_shoot_window):
                self.alien_shoot_time = 0
            return self.alien_shoot_time
            
        def collision_checks(self):
            # Player lasers
            if self.ship.sprite.lasers:
                for laser in self.ship.sprite.lasers:
                    # Obstacle Collisions
                    if pygame.sprite.spritecollide(laser, self.blocks, True):
                        laser.kill()

                    # Alien Collisions
                    if pygame.sprite.spritecollide(laser, self.aliens, True):
                        laser.kill()
                    if pygame.sprite.spritecollide(laser, self.aliens_alt, True):
                        laser.kill()

                    # UFO 
                    if pygame.sprite.spritecollide(laser, self.ufo, True):
                        laser.kill()
            
            # Alien Lasers
            if self.alien_lasers:
                for laser in self.alien_lasers:
                        if pygame.sprite.spritecollide(laser, self.blocks, True):
                            laser.kill()

                        if pygame.sprite.spritecollide(laser, self.ship, False):
                            laser.kill()
                            explode_sprite = Explosion(100, 100)
                            self.explode_alien.add(explode_sprite)
                            print('DEAD DEAD!!!')

                        if pygame.sprite.spritecollide(laser, self.ship.sprite.lasers, True):
                            laser.kill()

            # Aliens 
            if self.aliens:
                for alien in self.aliens:
                    pygame.sprite.spritecollide(alien, self.blocks, True)

                    


        def run(self):
            self.ship.update()
            self.aliens.update(self.alien_direction)
            self.aliens_alt.update(self.alien_direction)
            self.alien_lasers.update()
            self.ufo.update()
            
            self.ufo_timer()
            self.alien_position_checker()
            self.collision_checks()
            

            self.ship.sprite.lasers.draw(screen)
            self.ship.draw(screen)
            self.blocks.draw(screen)
            self.alien_lasers.draw(screen)
            self.ufo.draw(screen)
            self.explode_alien.draw(screen)
            
            flip_alien = self.get_delay_timer()
            if flip_alien > self.flip_time: 
                self.aliens.draw(screen)
            else:
                self.aliens_alt.draw(screen)

            delay_shoot = self.delay_alien_fire()
            if delay_shoot > self.alien_shoot_threshold:
                self.alien_shoot()

            #print(len(self.aliens_alt))
            #print(len(self.aliens))
            #print(len(self.alien_lasers))
           

"""
Program body and main loop
"""
if __name__ == '__main__':
    # Initialise Constants
    BLACK = (0, 0, 0)
    WHITE = (200, 200, 200)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 0, 255)
    CYAN = (0, 255, 255)
    # Gives a fake 4:3 monitor
    WINDOW_HEIGHT = 380
    WINDOW_WIDTH = 540
    MARGIN = 40
    SHIP_SPEED = 5

    # Pygame Initialise
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('py_invaders V1.0.0')
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Variables
    start = True
    fps = 60
    game = Game()


    # Main loop
    while start:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False

        # Set Frame Rate
        clock.tick(fps)

        # Erase Background
        screen.fill(BLACK)

        # Call Game Elements
        game.run()

        # Update display
        pygame.display.flip()


    pygame.quit()
