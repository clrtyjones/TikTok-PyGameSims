import pygame
import sys
import math
import random
import os
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
        self.trail = []  # List to store positions and radii for the trail

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

# Circle properties
circle_center = (width / 2, height / 2)
circle_radius = 475
circle_thickness = 7
visible_inner_radius = circle_radius - circle_thickness

# Initial positions for the balls
initial_positions = [(480.0, 795.0), (600.0, 795.0)]
initial_radius = 30
initial_velocities = [(0, 0), (0, 0)]  # Example initial velocities
ball1 = Ball(initial_positions[0][0], initial_positions[0][1], initial_velocities[0][0], initial_velocities[0][1], black, initial_radius)
ball2 = Ball(initial_positions[1][0], initial_positions[1][1], initial_velocities[1][0], initial_velocities[1][1], black, initial_radius)
balls = [ball1, ball2]
static_balls = []  # Store static balls in a separate list

# Gravity properties
gravity = 0.5  # Acceleration due to gravity
restitution = 1.0  # Bounciness factor

# Load sound
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
audio_dir = os.path.join(main_dir, "Audios")
audio_file = "pop.wav"
audio_path = os.path.join(audio_dir, audio_file)
original_sound = AudioSegment.from_file(audio_path)

# # Define export parameters
# output_format = "wav"  # Specify the desired output format, e.g., "mp3", "wav", etc.
# output_file_path = "output_audio." + output_format
# bitrate = "128k"  # Specify the desired bitrate, e.g., "64k", "128k", "192k", etc.
# sample_width = 2  # Specify the desired sample width in bytes, e.g., 1 (8-bit), 2 (16-bit), etc.
# channels = 2  # Specify the desired number of channels, e.g., 1 (mono), 2 (stereo), etc.
# target_db = -5  # Specify the desired target decibel level

# # Apply gain to adjust the volume level
# adjusted_audio = original_sound.apply_gain(target_db)

# # Export the audio with custom parameters
# adjusted_audio.export(output_file_path, format=output_format, bitrate=bitrate, parameters=["-ac", str(channels), "-sample_fmt", f's{8*sample_width}'])

# Prepare a list of pygame sounds with different pitches
pitch_semitones = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 22, 18, 16, 14, 12, 10, 8, 6, 4, 2]
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
    global circle_thickness, current_sound_index
    # Calculate the distance between the balls
    dist = distance(ball1, ball2)

    if dist < 2 * ball1.radius:
        
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
    # Calculate the distance between the ball and the static ball
    dist = distance(ball, static_ball)
    if dist < ball.radius + static_ball.radius:
        
        channel = play_collision_sound()
        if channel:
            channel.play(collision_sounds[current_sound_index])
        current_sound_index = (current_sound_index + 1) % len(collision_sounds)

        # Normal vector at the point of collision
        nx = (ball.x - static_ball.x) / dist
        ny = (ball.y - static_ball.y) / dist

        # Reflect the velocity vector
        dot_product = ball.vx * nx + ball.vy * ny
        ball.vx -= 2 * dot_product * nx
        ball.vy -= 2 * dot_product * ny

        # Apply restitution for bounciness
        ball.vx *= restitution
        ball.vy *= restitution

        # Reposition the ball to avoid sticking
        overlap = ball.radius + static_ball.radius - dist
        ball.x += overlap * nx
        ball.y += overlap * ny

def update_trails():
    # Add the current position and radius to the trail for each ball
    for ball in balls:
        ball.trail.append((ball.x, ball.y, ball.radius))

# Main game loop
running = True
paused = True  # Start the simulation paused
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
                start_time = pygame.time.get_ticks()  # Track the start time
            elif event.key == pygame.K_r:
                pygame.quit()
                sys.exit()

    if not paused:
        update_trails()

        for ball in balls:
            ball.vy += gravity  # Apply gravity to vertical velocity
            ball.x += ball.vx
            ball.y += ball.vy

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
        if elapsed_time >= 2930:
            new_static_balls = []
            for ball in balls:
                new_static_balls.append(Ball(ball.x, ball.y, 0, 0, black, ball.radius))
            static_balls.extend(new_static_balls)

            # Reset original balls to their initial positions with initial velocities
            ball1.x, ball1.y = initial_positions[0]
            ball1.vx, ball1.vy = initial_velocities[0]
            ball2.x, ball2.y = initial_positions[1]
            ball2.vx, ball2.vy = initial_velocities[1]

            # Clear trails
            ball1.trail.clear()
            ball2.trail.clear()

            start_time = pygame.time.get_ticks()  # Reset the timer

    # Fill the screen with black
    screen.fill(black)

    # Draw the balls' trails
    for ball in balls:
        for pos in ball.trail:
            # Draw the trail with a white outline
            pygame.draw.circle(screen, white, (int(pos[0]), int(pos[1])), pos[2] + 2)
            pygame.draw.circle(screen, ball.color, (int(pos[0]), int(pos[1])), pos[2])

    # Draw the balls with outlines
    for ball in balls:
        # Draw the outline
        pygame.draw.circle(screen, white, (int(ball.x), int(ball.y)), ball.radius + 1)
        # Draw the filled ball
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)

    # Draw static black balls with white outlines
    for static_ball in static_balls:
        pygame.draw.circle(screen, white, (int(static_ball.x), (int(static_ball.y))), static_ball.radius + 1)
        pygame.draw.circle(screen, static_ball.color, (int(static_ball.x), (int(static_ball.y))), static_ball.radius)

    # Draw the large circle in the middle first with outline
    pygame.draw.circle(screen, white, circle_center, circle_radius, circle_thickness)

    # Update the display
    pygame.display.flip()

    

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()