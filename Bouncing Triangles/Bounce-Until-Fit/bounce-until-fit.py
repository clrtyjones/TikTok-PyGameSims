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
initial_positions = [(540, 800)]
initial_radius = 35
initial_velocities = [(0, 0)]  # Example initial velocities
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
            #handle_boundary_collision(ball)

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

    # Draw the chevron using two polygons
    chevron_tip_x = width // 2
    chevron_tip_y = chevron_top_y + chevron_height
    chevron_bottom_y = chevron_tip_y + chevron_height


#---------------------------
#     TL
#        #
#        ##
#        ###
#        ####
#     BL  ####
#          ####
#           ####  TR
#            ####
#             ###
#              ##
#               #
#                 BR
#---------------------------


    left_rhombus = [
        # Top Right 
        (490, 900),
        # Top Left
        (100, 500),
        # Bottom Left
        (100, 550),
        # Bottom Right
        (490, 950)
    ]

    right_rhombus = [
        # Top Right 
        (980, 500),
        # Top Left
        (590, 900),
        # Bottom Left
        (590, 950),
        # Bottom Right
        (980, 550)
    ]

    pygame.draw.polygon(screen, white, left_rhombus)
    pygame.draw.polygon(screen, white, right_rhombus)

    # Draw the balls
    for ball in balls:
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()#
sys.exit()
