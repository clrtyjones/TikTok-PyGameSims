import pygame
import sys
import math
import random
import os
import colorsys
from pydub import AudioSegment
from pydub.playback import play

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
num_channels = 200  # Adjust this based on the number of simultaneous sounds you expect
pygame.mixer.set_num_channels(num_channels)

# Screen dimensions
width, height = 1080, 1920
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Ball Gets Bigger With Every Bounce")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 0, 255)
green = (0, 255, 85)

# Ball properties
initial_radius = 8
ball1 = Ball(540, 960, -2, 2, green, initial_radius)
balls = [ball1]  # Store all balls in a list

# Circle properties
circle_center = (width // 2, height // 2)
circle_radius = 475

# Gravity properties
gravity = 0.7  # Acceleration due to gravity
restitution = 0.97  # Bounciness factor

# Load sound
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
audio_dir = os.path.join(main_dir, "Audios")
audio_file = "synthB.wav"
audio_path = os.path.join(audio_dir, audio_file)
original_sound = AudioSegment.from_file(audio_path)

# Prepare a list of pygame sounds with different pitches
pitch_semitones = [-2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
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
    global circle_radius, current_sound_index, gravity, restitution
    # Calculate the distance from the ball to the circle center
    dist = math.hypot(ball.x - circle_center[0], ball.y - circle_center[1])
    if dist + ball.radius > circle_radius:
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
        overlap = dist + ball.radius - circle_radius
        ball.x -= overlap * nx
        ball.y -= overlap * ny

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

            # # Update hue and color for rainbow effect
            # ball.hue = (ball.hue + 2) % 360
            # ball.color = hsv_to_rgb(ball.hue / 360, 1.0, 1.0)

            # Handle collision with outer circle
            handle_boundary_collision(ball)

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
    pygame.draw.circle(screen, white, (540, 960), circle_radius, 2)

    # Define the finish line position and dimensions
    finish_line_y = height - 550  # Adjust the y-coordinate as needed
    block_height = 20  # Height of each block in the checkerboard
    num_blocks = 50  # Number of blocks in the checkerboard
    block_width = width // num_blocks  # Width of each block, spans the entire width

    # Draw the checkerboard finish line with white blocks
    for row in range(5):  # Draw 5 rows of the checkerboard
        y = finish_line_y + row * block_height
        for i in range(num_blocks + 20):
            x = i * block_width
            if (row + i) % 2 == 0:
                color = (200, 200, 200)  # White color
            else:
                color = black  # Background color (black in this case)
            pygame.draw.rect(screen, color, (x, y, block_width, block_height))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
