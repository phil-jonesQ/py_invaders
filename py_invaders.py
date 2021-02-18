""" py_invaders - space invaders clone coded in python with pygame
game assets credit - Benedict Gaster
"""

import pygame

# Initialise Constants
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 0, 255)
CYAN = (0, 255, 255)
# Gives a fake 4:3 monitor
WINDOW_HEIGHT = 480
WINDOW_WIDTH = 640
MARGIN = 40

# Pygame Initialise
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption('py_invaders V1.0.0')
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# Variables
start = True
fps = 60

class Ship:
    def __init__(self, x, y, colour, length):
        pass




# Main loop
while start:
    # Set Frame Rate
    clock.tick(fps)

    # Erase Background
    screen.fill(BLACK)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start = False

pygame.quit()
