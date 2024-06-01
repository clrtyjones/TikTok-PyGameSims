import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 607, 1080
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball")

x = 19
y = 19
speed_x = 4
speed_y = 4

# Probability of changing direction when hitting a wall (in percent)
change_direction_probability = 2  # Adjust as needed

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)

    pygame.draw.circle(screen, WHITE, (x, y), 20)

    x += speed_x
    y += speed_y

    # Check if the ball hits the left or right edge of the window
    if x > WIDTH - 20 or x < 20:
        speed_x *= -1

    # Check if the ball hits the top or bottom edge of the window
    if y > HEIGHT - 20 or y < 20:
        speed_y *= -1

    pygame.display.flip()
    pygame.time.Clock().tick(60)
