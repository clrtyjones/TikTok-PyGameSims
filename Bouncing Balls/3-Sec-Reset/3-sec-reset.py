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
        self.hue = 300

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
initial_radius = 20
initial_positions = [(490, 700), (590, 700)]
ball1 = Ball(initial_positions[0][0], initial_positions[0][1], 0, 0, white, initial_radius)
ball2 = Ball(initial_positions[1][0], initial_positions[1][1], 0, 0, white, initial_radius)
balls = [ball1, ball2]  # Store all balls in a list
static_balls = []  # Store static balls in a separate list

# Circle properties
circle_center = (width // 2, height // 2)
circle_radius = 475
circle_thickness = 7
visible_inner_radius = circle_radius - circle_thickness

# Gravity properties
gravity = 0.4  # Acceleration due to gravity
restitution = 1.0  # Bounciness factor

# Load sound
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
audio_dir = os.path.join(main_dir, "Audios")
audio_file = "pingpong.wav"
audio_path = os.path.join(audio_dir, audio_file)
original_sound = AudioSegment.from_file(audio_path)

# Prepare a list of pygame sounds with different pitches
pitch_semitones = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]
collision_sounds = [pydub_to_pygame(change_pitch(original_sound, semitone)) for semitone in pitch_semitones]
current_sound_index = 0

# Time properties
clock = pygame.time.Clock()
fps = 60
start_time = 0  # Initialize start time

# Function to play collision sound on an available channel
def play_collision_sound():
    for i in range(pygame.mixer.get_num_channels()):
        if not pygame.mixer.Channel(i).get_busy():
            return pygame.mixer.Channel(i)
    return None

def distance(ball1, ball2):
    return math.hypot(ball1.x - ball2.x, ball1.y - ball2.y)

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

def handle_collision(ball1, ball2):
    global circle_thickness, visible_inner_radius, current_sound_index
    # Calculate the distance between the balls
    dist = distance(ball1, ball2)
    if dist < 2 * ball1.radius:
        visible_inner_radius = circle_radius - circle_thickness
        
        channel = play_collision_sound()
        if channel:
            channel.play(collision_sounds[current_sound_index])
        current_sound_index = (current_sound_index + 1) % len(collision_sounds)

        # Calculate the normal and tangent vectors
        nx = (ball2.x - ball1.x) / dist
        ny = (ball2.y - ball1.y) / dist
        tx = -ny
        ty = nx

        # Dot products of velocities with the normal and tangent vectors
        v1n = nx * ball1.vx + ny * ball1.vy
        v1t = tx * ball1.vx + ty * ball1.vy
        v2n = nx * ball2.vx + ny * ball2.vy
        v2t = tx * ball2.vx + ty * ball2.vy

        # Swap the normal components of the velocities (elastic collision)
        ball1.vx = v2n * nx + v1t * tx
        ball1.vy = v2n * ny + v1t * ty
        ball2.vx = v1n * nx + v2t * tx
        ball2.vy = v1n * ny + v2t * ty

        # Separate the balls to prevent sticking
        overlap = 2 * ball1.radius - dist
        ball1.x -= overlap / 2 * nx
        ball1.y -= overlap / 2 * ny
        ball2.x += overlap / 2 * nx
        ball2.y += overlap / 2 * ny

def handle_static_ball_collision(ball, static_ball):
    global current_sound_index
    dist = distance(ball, static_ball)
    if dist < ball.radius + static_ball.radius:
        channel = play_collision_sound()
        if channel:
            channel.play(collision_sounds[current_sound_index])
        current_sound_index = (current_sound_index + 1) % len(collision_sounds)

        nx = (ball.x - static_ball.x) / dist
        ny = (ball.y - static_ball.y) / dist

        dot_product = ball.vx * nx + ball.vy * ny
        ball.vx -= 2 * dot_product * nx
        ball.vy -= 2 * dot_product * ny

        ball.vx *= restitution
        ball.vy *= restitution

        overlap = ball.radius + static_ball.radius - dist
        ball.x += overlap * nx
        ball.y += overlap * ny

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color space."""
    rgb = colorsys.hsv_to_rgb(h, s, v)
    return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def update_trails():
    for ball in balls:
        ball.trail.append((ball.x, ball.y, ball.color, ball.radius))
        # Limit the length of the trail for performance and visual reasons
        if len(ball.trail) > 25:
            ball.trail.pop(0)

# Main game loop
running = True
paused = True  # Start the simulation paused
start_time = pygame.time.get_ticks()  # Track the start time
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

            # Handle collision with other balls
            for other_ball in balls:
                if ball != other_ball:
                    handle_collision(ball, other_ball)

            # Handle collision with static balls
            for static_ball in static_balls:
                handle_static_ball_collision(ball, static_ball)

            # Handle collision with outer circle
            handle_boundary_collision(ball)

        # Add new static balls every 3 seconds
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time > 3000:
            new_static_balls = []
            for ball in balls:
                new_static_balls.append(Ball(ball.x, ball.y, 0, 0, white, ball.radius))
            static_balls.extend(new_static_balls)

            # Reset original balls to their initial positions with 0 velocity
            ball1.x, ball1.y = initial_positions[0]
            ball1.vx, ball1.vy = 0, 0
            ball2.x, ball2.y = initial_positions[1]
            ball2.vx, ball2.vy = 0, 0

            start_time = pygame.time.get_ticks()  # Reset the timer

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

    # Draw static white balls with outlines
    for static_ball in static_balls:
        pygame.draw.circle(screen, black, (int(static_ball.x), int(static_ball.y)), static_ball.radius + 2)
        pygame.draw.circle(screen, static_ball.color, (int(static_ball.x), int(static_ball.y)), static_ball.radius)

    # Draw the large circle in the middle first with outline
    pygame.draw.circle(screen, white, circle_center, circle_radius, circle_thickness)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
