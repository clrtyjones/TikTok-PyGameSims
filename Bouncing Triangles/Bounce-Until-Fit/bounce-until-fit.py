import pygame
import sys
import math
import os
import random
from pydub import AudioSegment
from pydub.playback import play
from pydub.generators import Sine
import simpleaudio as sa
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
        self.trail = []  # List to store positions and radii for the trail
        self.hue = random.randint(0, 360)  # Initialize with a random hue value

# Initialize Pygame
pygame.init()

# Initialize mixer and allocate multiple channels
pygame.mixer.init()
num_channels = 75  # Adjust this based on the number of simultaneous sounds you expect
pygame.mixer.set_num_channels(num_channels)

# Screen dimensions
width, height = 1080, 1920
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Ball Bouncing Over Chevron")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Chevron properties
chevron_top_y = height // 3
chevron_width = width // 2
chevron_height = chevron_width // 2
chevron_cutoff = 100  # Width of the cut-off at the tip

# Initial positions for the balls
initial_positions = [(width // 2, 100)]
initial_radius = 35
initial_velocities = [(10, -5)]  # Example initial velocities
ball1 = Ball(initial_positions[0][0], initial_positions[0][1], initial_velocities[0][0], initial_velocities[0][1], white, initial_radius)
balls = [ball1]

# Gravity properties
gravity = 0.5  # Acceleration due to gravity
restitution = 0.9  # Bounciness factor

# Load sound
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
audio_dir = os.path.join(main_dir, "Audios")
audio_file = "pingpong.wav"
audio_path = os.path.join(audio_dir, audio_file)
original_sound = AudioSegment.from_file(audio_path)

# Time properties
clock = pygame.time.Clock()
fps = 60

# Initialize font
font = pygame.font.SysFont(None, 36)

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

# Prepare a list of pygame sounds with different pitches
pitch_semitones = [0, 1 ,2 ,3 ,4 ,5, 6]
collision_sounds = [pydub_to_pygame(change_pitch(original_sound, semitone)) for semitone in pitch_semitones]
current_sound_index = 0

# Function to play collision sound on an available channel
def play_collision_sound():
    for i in range(pygame.mixer.get_num_channels()):
        if not pygame.mixer.Channel(i).get_busy():
            return pygame.mixer.Channel(i)
    return None

# Simplified game loop
running = True
paused = True  # Start the simulation paused
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    if not paused:
        for ball in balls:
            ball.vy += gravity  # Apply gravity to vertical velocity
            ball.x += ball.vx
            ball.y += ball.vy

            # Update hue and color for rainbow effect
            ball.hue = (ball.hue + 2) % 360
            ball.color = hsv_to_rgb(ball.hue / 360, 1.0, 1.0)

    # Fill the screen with black
    screen.fill(black)

    # Draw the chevron
    chevron_points = [
        ((width // 2) - (chevron_width // 2), chevron_top_y),
        ((width // 2) + (chevron_width // 2), chevron_top_y),
        ((width // 2) + (chevron_width // 2) - chevron_cutoff // 2, chevron_top_y + chevron_height),
        ((width // 2) - (chevron_width // 2) + chevron_cutoff // 2, chevron_top_y + chevron_height)
    ]
    pygame.draw.polygon(screen, white, chevron_points)

    # Draw the balls
    for ball in balls:
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
