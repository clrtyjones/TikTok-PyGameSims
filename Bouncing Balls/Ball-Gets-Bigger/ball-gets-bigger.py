import pygame
import sys
import math
import random
import os
import colorsys
from pydub import AudioSegment
from pydub.playback import play
import io

os.environ["SDL_VIDEODRIVER"] = "dummy"  # Use dummy driver to prevent SDL from loading default drivers
os.environ["SDL_VIDEO_CENTERED"] = "1"   # Center the window

# Use OpenGL for rendering
os.environ["SDL_VIDEODRIVER"] = "windib"
os.environ["SDL_VIDEO_X11_VISUALID"] = "0"

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

# Function to change the pitch of a sound
def change_pitch(sound, semitones):
    return sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * (2.0 ** (semitones / 12.0)))
    }).set_frame_rate(sound.frame_rate)

# Function to convert pydub sound to pygame sound
def pydub_to_pygame(sound):
    raw = sound.raw_data
    pygame_sound = pygame.mixer.Sound(buffer=raw)
    return pygame_sound

# Initialize Pygame
pygame.init()

# Initialize mixer and allocate multiple channels
pygame.mixer.init()
num_channels = 75  # Adjust this based on the number of simultaneous sounds you expect
pygame.mixer.set_num_channels(num_channels)

# Screen dimensions
width, height = 1080, 1920
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Ball Gets Bigger With Every Bounce")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Ball properties
initial_radius = 5
ball1 = Ball(540, 700, 0.1, -8.38, white, initial_radius)
balls = [ball1]  # Store all balls in a list

# Circle properties
circle_center = (width // 2, height // 2)
circle_radius = 475
circle_thickness = 7
visible_inner_radius = circle_radius - circle_thickness

# Gravity properties
gravity = 0.7  # Acceleration due to gravity
restitution = 1.005  # Bounciness factor

# Load sound
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
audio_dir = os.path.join(main_dir, "Audios")
audio_file = "boowomp.mp3"
audio_path = os.path.join(audio_dir, audio_file)
original_sound = AudioSegment.from_file(audio_path)

# Prepare a list of pygame sounds with different pitches
pitch_semitones = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]
collision_sounds = [pydub_to_pygame(change_pitch(original_sound, semitone)) for semitone in pitch_semitones]
current_sound_index = 0

# Time properties
clock = pygame.time.Clock()
fps = 60

# Function to play collision sound on an available channel
def play_collision_sound():
    for i in range(pygame.mixer.get_num_channels()):
        if not pygame.mixer.Channel(i).get_busy():
            return pygame.mixer.Channel(i)
    return None

def handle_boundary_collision(ball):
    global circle_thickness, visible_inner_radius, current_sound_index, gravity, restitution
    # Calculate the distance from the ball to the circle center
    dist = math.hypot(ball.x - circle_center[0], ball.y - circle_center[1])
    if dist + ball.radius > visible_inner_radius:
        visible_inner_radius = circle_radius - circle_thickness

        channel = play_collision_sound()
        if channel:
            channel.play(collision_sounds[current_sound_index])
        current_sound_index = (current_sound_index + 1) % len(collision_sounds)

        if ball.radius > 80:
            ball.radius += 2
        else:
            ball.radius += 1

        if ball.radius > 145:
            restitution = 1.005
            ball.radius += 2.75
        elif ball.radius > 45:
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
        if len(ball.trail) > 25:
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
            ball.hue = (ball.hue + 2) % 360
            ball.color = hsv_to_rgb(ball.hue / 360, 1.0, 1.0)

            # Handle collision with outer circle
            handle_boundary_collision(ball)
        
        # Check for collision with outer circle and spawn new balls
        if len(balls) < 2:
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
