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

# Initial positions for the balls
initial_positions = [(940, 500)]
initial_radius = 75
initial_velocities = [(-10, -10)]  # Example initial velocities
ball1 = Ball(initial_positions[0][0], initial_positions[0][1], initial_velocities[0][0], initial_velocities[0][1], white, initial_radius)
balls = [ball1]


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
    (500, 1150),
    # Top Left
    (-50, 700),
    # Bottom Left
    (-50, 750),
    # Bottom Right
    (500, 1200)
]

right_rhombus = [
    # Top Right 
    (1130, 700),
    # Top Left
    (580, 1150),
    # Bottom Left
    (580, 1200),
    # Bottom Right
    (1130, 750)
]


# Gravity properties
gravity = 0.4  # Acceleration due to gravity
restitution = 0.95  # Bounciness factor

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

# Function to handle collision with window walls
def handle_wall_collision(ball):
    # Left wall
    if ball.x - ball.radius <= 0:
        ball.vx = abs(ball.vx)  # Change the direction of velocity
        ball.x = ball.radius  # Move the ball inside the window
        ball.radius -= 1
    # Right wall
    elif ball.x + ball.radius >= width:
        ball.vx = -abs(ball.vx)  # Change the direction of velocity
        ball.x = width - ball.radius  # Move the ball inside the window
        ball.radius -= 1

# Function to handle collision between ball and polygon
def handle_collision(ball, polygon):
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        # Check if ball intersects with the edge p1-p2
        if point_line_distance(ball, p1, p2) <= ball.radius:

            # Update Ball Size -1
            ball.radius -= 1

            # Calculate normal vector of the edge
            edge_vector = (p2[0] - p1[0], p2[1] - p1[1])
            edge_length = math.sqrt(edge_vector[0]**2 + edge_vector[1]**2)
            normal_vector = (-edge_vector[1] / edge_length, edge_vector[0] / edge_length)
            # Reflect ball velocity
            dot_product = ball.vx * normal_vector[0] + ball.vy * normal_vector[1]
            ball.vx -= 2 * dot_product * normal_vector[0]
            ball.vy -= 2 * dot_product * normal_vector[1]
            # Apply restitution
            ball.vx *= restitution
            ball.vy *= restitution
            # Correct ball position to avoid sticking
            overlap = ball.radius - point_line_distance(ball, p1, p2)
            ball.x += normal_vector[0] * overlap
            ball.y += normal_vector[1] * overlap
            # Play collision sound
            channel = play_collision_sound()
            if channel:
                global current_sound_index
                channel.play(collision_sounds[current_sound_index])
                current_sound_index = (current_sound_index + 1) % len(collision_sounds)
            break

def point_line_distance(ball, p1, p2):
    """Calculate the distance from the ball center to the line segment p1-p2."""
    px, py = ball.x, ball.y
    x1, y1 = p1
    x2, y2 = p2
    line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if line_length == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2)
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length**2))
    projection = (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return math.sqrt((px - projection[0])**2 + (py - projection[1])**2)

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

            # Handle collision with window walls
            handle_wall_collision(ball)

            # Handle collision with polygons
            handle_collision(ball, left_rhombus)
            handle_collision(ball, right_rhombus)

            # Update position
            ball.x += ball.vx
            ball.y += ball.vy

            # Update hue and color for rainbow effect
            ball.hue = (ball.hue + 2) % 360
            ball.color = hsv_to_rgb(ball.hue / 360, 1.0, 1.0)

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

    # Draw the polygons
    pygame.draw.polygon(screen, white, left_rhombus)
    pygame.draw.polygon(screen, white, right_rhombus)

    # Draw the balls
    for ball in balls:
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)

    # Render text surface
    text_surface = font.render("Ball Size: {}".format(ball1.radius), True, white)
    # Get the rectangle of the text surface
    text_rect = text_surface.get_rect()
    # Position the text rectangle at the bottom center of the screen
    text_rect.midbottom = (width // 2, (height // 2) + 400)
    # Draw text surface onto the screen
    screen.blit(text_surface, text_rect)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
