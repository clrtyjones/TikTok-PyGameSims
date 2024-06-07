import pygame
import sys
import math
import os
from pydub import AudioSegment
from pydub.playback import play
from pydub.generators import Sine
import simpleaudio as sa
import time

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
pygame.display.set_caption("Balls Reset Every 3 Seconds, No Collision")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Circle properties
circle_center = (width / 2, height / 2)
circle_radius = 475
circle_thickness = 7
visible_inner_radius = circle_radius - circle_thickness

# Initial positions for the balls
initial_positions = [(440.0, 650.0), (640.0, 650.0)]
initial_radius = 35
initial_velocities = [(10, -5), (-10, -5)]  # Example initial velocities
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
audio_file = "boom.wav"
audio_path = os.path.join(audio_dir, audio_file)
original_sound = AudioSegment.from_file(audio_path)

# Prepare a list of pygame sounds with different pitches
pitch_semitones = [0, 1 ,2 ,3 ,4 ,5, 6]
collision_sounds = [pydub_to_pygame(change_pitch(original_sound, semitone)) for semitone in pitch_semitones]
current_sound_index = 0

# Time properties
clock = pygame.time.Clock()
fps = 60
start_time = 0  # Initialize start time

# Initialize font
font = pygame.font.SysFont(None, 36)

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

# Function to generate rainbow colors
def rainbow_color(time, offset=0):
    frequency = 0.6
    r = int(math.sin(frequency * time + 0 + offset) * 127 + 128)
    g = int(math.sin(frequency * time + 2 + offset) * 127 + 128)
    b = int(math.sin(frequency * time + 4 + offset) * 127 + 128)
    return (r, g, b)

# Main game loop
running = True
paused = True  # Start the simulation paused
countdown = 3  # Initialize countdown
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

            # Handle collision with static balls
            for static_ball in static_balls:
                handle_static_ball_collision(ball, static_ball)

            # Handle collision with outer circle
            handle_boundary_collision(ball)

        # Calculate countdown
        elapsed_time = pygame.time.get_ticks() - start_time
        countdown = 3 - (elapsed_time // 1000)
        
        # Add new static balls every 3 seconds
        if elapsed_time >= 3000:
            current_sound_index = 0
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
    time = pygame.time.get_ticks() / 1000  # Get the current time in seconds
    for ball in balls:
        for i, pos in enumerate(ball.trail):
            trail_color = rainbow_color(time, offset=i * 0.1)  # Get the rainbow color with an offset
            pygame.draw.circle(screen, black, (int(pos[0]), int(pos[1])), pos[2] + 2)
            pygame.draw.circle(screen, trail_color, (int(pos[0]), int(pos[1])), pos[2])

    # Draw the balls with outlines
    for ball in balls:
        ball_color = rainbow_color(time)
        # Draw the outline
        pygame.draw.circle(screen, black, (int(ball.x), int(ball.y)), ball.radius + 1)
        # Draw the filled ball
        pygame.draw.circle(screen, ball_color, (int(ball.x), int(ball.y)), ball.radius)

        # Render and draw countdown text
        countdown_text = font.render(str(countdown), True, white)
        text_rect = countdown_text.get_rect(center=(ball.x, ball.y))
        screen.blit(countdown_text, text_rect)

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
