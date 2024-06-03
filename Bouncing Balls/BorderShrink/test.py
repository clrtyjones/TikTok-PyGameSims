import pygame
import sys
import math
import random
import os

# Ball Class
class Ball:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 607, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("3 Second Ball Simulation")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Ball properties
ball_radius = 10
ball1 = Ball(253.5, 500, -4, -15, white)
ball2 = Ball(353.5, 500, 4, -15, white)
balls = [ball1, ball2]  # Store all balls in a list

# Circle properties
circle_center = (width // 2, height // 2)
circle_radius = 275
circle_thickness = 2
visible_inner_radius = circle_radius - circle_thickness

# Gravity properties
gravity = 0.3  # Acceleration due to gravity
restitution = 1.0  # Bounciness factor

# Load sound
current_dir = os.path.dirname(os.path.abspath(__file__))
audio_file = "metallic-impact.wav"
audio_path = os.path.join(current_dir, audio_file)
collision_sound = pygame.mixer.Sound(audio_path)

# Time properties
clock = pygame.time.Clock()
fps = 60

def distance(ball1, ball2):
    return math.hypot(ball1['x'] - ball2['x'], ball1['y'] - ball2['y'])

def handle_collision(ball1, ball2):
    global circle_thickness, visible_inner_radius
    # Calculate the distance between the balls
    dist = distance(ball1, ball2)
    if dist < 2 * ball_radius:

        circle_thickness += 1
        visible_inner_radius = circle_radius - circle_thickness

        collision_sound.play()
        
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

        # Change Color Of Ball For Every Collision
        ball1['color'] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        ball2['color'] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def handle_boundary_collision(ball):
    global circle_thickness, visible_inner_radius
    # Calculate the distance from the ball to the circle center
    dist = math.hypot(ball['x'] - circle_center[0], ball['y'] - circle_center[1])
    if dist + ball_radius > visible_inner_radius:

        circle_thickness += 1
        visible_inner_radius = circle_radius - circle_thickness

        collision_sound.play()

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
        overlap = dist + ball_radius - visible_inner_radius
        ball['x'] -= overlap * nx
        ball['y'] -= overlap * ny

        # Change Color Of Ball For Every Collision
        ball['color'] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def spawn_new_ball():
    # Generate random coordinates within the circle
    angle = random.uniform(0, math.pi * 2)
    spawn_radius = random.uniform(0, visible_inner_radius - ball_radius)
    spawn_x = circle_center[0] + math.cos(angle) * spawn_radius
    spawn_y = circle_center[1] + math.sin(angle) * spawn_radius

    # Generate random velocities
    vx = random.uniform(-5, 5)
    vy = random.uniform(-20, -5)  # Ensure the ball moves upwards initially

    # Random color
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    return Ball(spawn_x, spawn_y, vx, vy, color)


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
        for ball in balls:
            # Apply gravity
            ball.vy += gravity

            # Update position
            ball.x += ball.vx
            ball.y += ball.vy

            # Handle collision with other balls
            for other_ball in balls:
                if ball != other_ball:
                    handle_collision(ball, other_ball)

            # Handle collision with outer circle
            handle_boundary_collision(ball)
        
        # Check for collision with outer circle and spawn new balls
        if len(balls) < 3:  # Limiting to 3 balls for demonstration
            for ball in balls.copy():
                dist = math.hypot(ball.x - circle_center[0], ball.y - circle_center[1])
                if dist + ball_radius > visible_inner_radius:
                    balls.append(spawn_new_ball())

    # Fill the screen with black
    screen.fill(black)

    # Draw the large circle in the middle
    pygame.draw.circle(screen, white, circle_center, circle_radius, circle_thickness)

    # Draw the balls
    for ball in balls:
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball_radius)


    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
