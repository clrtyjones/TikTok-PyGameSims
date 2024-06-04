import pygame
import sys
import math
import random
import os
import colorsys

# Ball Class
class Ball:
    def __init__(self, x, y, vx, vy, color, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.trail = []  # List to store positions, colors, and radii for the trail
        self.hue = random.randint(0, 360)  # Initialize with a random hue value

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
initial_radius = 5
ball1 = Ball(303.5, 500, 1, -12, white, initial_radius)
balls = [ball1]  # Store all balls in a list

# Circle properties
circle_center = (width // 2, height // 2)
circle_radius = 275
circle_thickness = 2
visible_inner_radius = circle_radius - circle_thickness

# Gravity properties
gravity = 0.4  # Acceleration due to gravity
restitution = 1.001  # Bounciness factor

# Load sound
current_dir = os.path.dirname(os.path.abspath(__file__))
audio_file = "pingpong.wav"
audio_path = os.path.join(current_dir, audio_file)
collision_sound = pygame.mixer.Sound(audio_path)

# Time properties
clock = pygame.time.Clock()
fps = 60

def handle_boundary_collision(ball):
    global circle_thickness, visible_inner_radius
    # Calculate the distance from the ball to the circle center
    dist = math.hypot(ball.x - circle_center[0], ball.y - circle_center[1])
    if dist + ball.radius > visible_inner_radius:
        visible_inner_radius = circle_radius - circle_thickness
        collision_sound.play()

        ball.radius += 2

        # Normal vector at the point of collision
        nx = (ball.x - circle_center[0]) / dist
        ny = (ball.y - circle_center[1]) / dist

        # Reflect the velocity vector
        dot_product = ball.vx * nx + ball.vy * ny
        ball.vx -= 2 * dot_product * nx
        ball.vy -= 2 * dot_product * ny

        # Apply restitution for bounciness
        ball.vx *= restitution
        ball.vy *= restitution

        # Reposition the ball to avoid sticking
        overlap = dist + ball.radius - visible_inner_radius
        ball.x -= overlap * nx
        ball.y -= overlap * ny

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color space."""
    rgb = colorsys.hsv_to_rgb(h, s, v)
    return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def spawn_new_ball():
    # Generate random coordinates within the circle
    angle = random.uniform(0, math.pi * 2)
    spawn_radius = random.uniform(0, visible_inner_radius - initial_radius)
    spawn_x = circle_center[0] + math.cos(angle) * spawn_radius
    spawn_y = circle_center[1] + math.sin(angle) * spawn_radius

    # Generate random velocities
    vx = random.uniform(-5, 5)
    vy = random.uniform(-20, -5)  # Ensure the ball moves upwards initially

    # Random color
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    return Ball(spawn_x, spawn_y, vx, vy, color, initial_radius)

def update_trails():
    for ball in balls:
        ball.trail.append((ball.x, ball.y, ball.color, ball.radius))
        # Limit the length of the trail for performance and visual reasons
        if len(ball.trail) > 100:
            ball.trail.pop(0)

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
        update_trails()
        for ball in balls:
            # Apply gravity
            ball.vy += gravity

            # Update position
            ball.x += ball.vx
            ball.y += ball.vy

            # Update hue and color for rainbow effect
            ball.hue = (ball.hue + 1) % 360
            ball.color = hsv_to_rgb(ball.hue / 360, 1.0, 1.0)

            # Handle collision with outer circle
            handle_boundary_collision(ball)
        
        # Check for collision with outer circle and spawn new balls
        if len(balls) > 2:
            for ball in balls.copy():
                dist = math.hypot(ball.x - circle_center[0], ball.y - circle_center[1])
                if dist + ball.radius > visible_inner_radius:
                    balls.append(spawn_new_ball())

    # Fill the screen with black
    screen.fill(black)

    # Draw the balls' trails with outlines
    for ball in balls:
        for i, pos in enumerate(ball.trail):
            fade_power = 5.5  # Adjust the power to control the rate of fade away
            alpha = int(255 * ((i / len(ball.trail)) ** fade_power))
            trail_color = (*pos[2], alpha)
            # Draw the outline for the trail
            trail_surface = pygame.Surface((pos[3]*2+4, pos[3]*2+4), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (0, 0, 0, alpha), (pos[3]+2, pos[3]+2), pos[3] + 2)
            # Draw the filled trail ball
            pygame.draw.circle(trail_surface, trail_color, (pos[3]+2, pos[3]+2), pos[3])
            screen.blit(trail_surface, (int(pos[0] - pos[3] - 2), int(pos[1] - pos[3] - 2)))

    # Draw the balls with outlines
    for ball in balls:
        # Draw the outline
        pygame.draw.circle(screen, black, (int(ball.x), int(ball.y)), ball.radius + 2)
        # Draw the filled ball
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)

    # Draw the large circle in the middle first with outline
    pygame.draw.circle(screen, white, circle_center, circle_radius, circle_thickness)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
