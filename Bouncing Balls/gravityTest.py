import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 607, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ball Collision Simulation")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Ball properties
ball_radius = 20
ball1 = {'x': 253.5, 'y': 500, 'vx': 5, 'vy': 2, 'color': white}
ball2 = {'x': 353.5, 'y': 500, 'vx': -5, 'vy': -2, 'color': white}

# Circle properties
circle_center = (width // 2, height // 2)
circle_radius = 200

# Gravity properties
gravity = 0.5  # Acceleration due to gravity
restitution = 1.0  # Bounciness factor

# Time properties
clock = pygame.time.Clock()
fps = 60

def distance(ball1, ball2):
    return math.hypot(ball1['x'] - ball2['x'], ball1['y'] - ball2['y'])

def handle_collision(ball1, ball2):
    # Calculate the distance between the balls
    dist = distance(ball1, ball2)
    if dist < 2 * ball_radius:
        # Calculate the normal and tangent vectors
        nx = (ball2['x'] - ball1['x']) / dist
        ny = (ball2['y'] - ball1['y']) / dist
        tx = -ny
        ty = nx

        # Dot products of velocities with the normal and tangent vectors
        v1n = nx * ball1['vx'] + ny * ball1['vy']
        v1t = tx * ball1['vx'] + ty * ball1['vy']
        v2n = nx * ball2['vx'] + ny * ball2['vy']
        v2t = tx * ball2['vx'] + ty * ball2['vy']

        # Swap the normal components of the velocities (elastic collision)
        ball1['vx'] = v2n * nx + v1t * tx
        ball1['vy'] = v2n * ny + v1t * ty
        ball2['vx'] = v1n * nx + v2t * tx
        ball2['vy'] = v1n * ny + v2t * ty

        # Separate the balls to prevent sticking
        overlap = 2 * ball_radius - dist
        ball1['x'] -= overlap / 2 * nx
        ball1['y'] -= overlap / 2 * ny
        ball2['x'] += overlap / 2 * nx
        ball2['y'] += overlap / 2 * ny

def handle_boundary_collision(ball):
    # Calculate the distance from the ball to the circle center
    dist = math.hypot(ball['x'] - circle_center[0], ball['y'] - circle_center[1])
    if dist + ball_radius > circle_radius:
        # Normal vector at the point of collision
        nx = (ball['x'] - circle_center[0]) / dist
        ny = (ball['y'] - circle_center[1]) / dist

        # Reflect the velocity vector
        dot_product = ball['vx'] * nx + ball['vy'] * ny
        ball['vx'] -= 2 * dot_product * nx
        ball['vy'] -= 2 * dot_product * ny

        # Apply restitution for bounciness
        ball['vx'] *= restitution
        ball['vy'] *= restitution

        # Reposition the ball to avoid sticking
        overlap = dist + ball_radius - circle_radius
        ball['x'] -= overlap * nx
        ball['y'] -= overlap * ny

# Main game loop
running = True
paused = True  # Start the simulation paused
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # Check for key press to unpause
            paused = False

    if not paused:
        # Apply gravity to the balls' velocities
        ball1['vy'] += gravity
        ball2['vy'] += gravity

        # Update the balls' positions
        ball1['x'] += ball1['vx']
        ball1['y'] += ball1['vy']
        ball2['x'] += ball2['vx']
        ball2['y'] += ball2['vy']

        # Handle collision between the balls
        handle_collision(ball1, ball2)

        # Handle collision with the circle boundary
        handle_boundary_collision(ball1)
        handle_boundary_collision(ball2)

    # Fill the screen with black
    screen.fill(black)

    # Draw the large circle in the middle
    pygame.draw.circle(screen, white, circle_center, circle_radius, 2)

    # Draw the balls
    pygame.draw.circle(screen, ball1['color'], (int(ball1['x']), int(ball1['y'])), ball_radius)
    pygame.draw.circle(screen, ball2['color'], (int(ball2['x']), int(ball2['y'])), ball_radius)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
