import pygame
import sys
import math
import os
import random
import colorsys
from pydub import AudioSegment

# Square Class
class Square:
    def __init__(self, x, y, vx, vy, color, side_length):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.side_length = side_length
        self.trail = []  # List to store positions and vertices for the trail
        self.hue = random.randint(0, 360)  # Initialize with a random hue value
        self.angle = 0  # Initial angle of the square
        self.angular_velocity = 0  # Initial rotational velocity

    def get_vertices(self):
        # Calculate the vertices of the square based on its center (x, y), side length, and angle
        half_side = self.side_length / 2
        vertices = []
        for i in range(4):
            theta = math.radians(self.angle + i * 90)
            vertices.append((
                self.x + math.cos(theta) * half_side,
                self.y + math.sin(theta) * half_side
            ))
        return vertices

# Initialize Pygame
pygame.init()

# Initialize mixer and allocate multiple channels
pygame.mixer.init()
num_channels = 75  # Adjust this based on the number of simultaneous sounds you expect
pygame.mixer.set_num_channels(num_channels)

# Screen dimensions
width, height = 1080, 1920
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Square Bouncing Over Chevron")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 0, 255)
green = (0, 255, 85)

# Initial positions for the squares
initial_positions = [(140, 300), (940, 300)]
initial_side_length = 200
initial_velocities = [(0, 0)]  # Example initial velocities for both squares
square1 = Square(initial_positions[0][0], initial_positions[0][1], initial_velocities[0][0], initial_velocities[0][1], pink, initial_side_length)
square2 = Square(initial_positions[1][0], initial_positions[1][1], initial_velocities[0][0], initial_velocities[0][0], green, initial_side_length)
squares = [square1, square2]

# Gravity properties
gravity = 0.7  # Acceleration due to gravity
restitution = 0.97  # Bounciness factor

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
    (-150, 450),
    # Bottom Left
    (-150, 500),
    # Bottom Right
    (500, 1200)
]

right_rhombus = [
    # Top Right 
    (1230, 450),
    # Top Left
    (580, 1150),
    # Bottom Left
    (580, 1200),
    # Bottom Right
    (1230, 500)
]

# Load sound
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
audio_dir = os.path.join(main_dir, "Audios")
audio_file = "pop.wav"
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
pitch_semitones = [8, 6, 4]
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
    for square in squares:
        square.trail.append((square.x, square.y, square.color, square.get_vertices(), square.side_length))
        # Limit the length of the trail for performance and visual reasons
        if len(square.trail) > 30:
            square.trail.pop(0)

# Function to handle collision with window walls
def handle_wall_collision(square):
    # Calculate the bounding box of the square
    min_x = min(vertex[0] for vertex in square.get_vertices())
    max_x = max(vertex[0] for vertex in square.get_vertices())

    # Left wall
    if min_x <= 0:
        square.vx = abs(square.vx)  # Change the direction of velocity
        square.x += abs(min_x)  # Move the square inside the window
        square.side_length -= 1
        square.angular_velocity = random.uniform(-5, 5)  # Apply a random rotational velocity on collision
        square.vx *= restitution
        square.vy *= restitution
    # Right wall
    elif max_x >= width:
        square.vx = -abs(square.vx)  # Change the direction of velocity
        square.x -= (max_x - width)  # Move the square inside the window
        square.side_length -= 1
        square.angular_velocity = random.uniform(-5, 5)  # Apply a random rotational velocity on collision
        square.vx *= restitution
        square.vy *= restitution

# Function to handle collision between square and polygon
def handle_polygon_collision(square, polygon):
    offset = 2  # Small offset to prevent sticking
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        for j in range(4):
            v1 = square.get_vertices()[j]
            v2 = square.get_vertices()[(j + 1) % 4]
            if line_intersect(p1, p2, v1, v2):
                square.side_length -= 1
                edge_vector = (p2[0] - p1[0], p2[1] - p1[1])
                edge_length = math.sqrt(edge_vector[0]**2 + edge_vector[1]**2)
                normal_vector = (-edge_vector[1] / edge_length, edge_vector[0] / edge_length)
                dot_product = square.vx * normal_vector[0] + square.vy * normal_vector[1]
                square.vx -= 2 * dot_product * normal_vector[0]
                square.vy -= 2 * dot_product * normal_vector[1]
                square.vx *= restitution
                square.vy *= restitution
                square.angular_velocity = random.uniform(-5, 5)

                # Apply the offset to move the square away from the polygon
                square.x += normal_vector[0] * offset
                square.y += normal_vector[1] * offset

                channel = play_collision_sound()
                if channel:
                    global current_sound_index
                    channel.play(collision_sounds[current_sound_index])
                    current_sound_index = (current_sound_index + 1) % len(collision_sounds)
                return

# Function to handle collision between two squares
def handle_square_collision(square1, square2):
    # Calculate the distance between the centers of the squares
    dx = square2.x - square1.x
    dy = square2.y - square1.y
    distance = math.sqrt(dx**2 + dy**2)

    # Check if the squares are colliding
    if distance < (square1.side_length / 2 + square2.side_length / 2):
        square1.side_length -= 1
        square2.side_length -= 1
        # Calculate the normal vector
        normal_vector = (dx / distance, dy / distance)

        # Relative velocity
        rel_vx = square2.vx - square1.vx
        rel_vy = square2.vy - square1.vy
        rel_velocity = rel_vx * normal_vector[0] + rel_vy * normal_vector[1]

        # Do not resolve if the squares are moving apart
        if rel_velocity > 0:
            return

        # Impulse scalar
        impulse = (-(1 + restitution) * rel_velocity) / 2

        # Apply impulse to the velocities
        square1.vx -= impulse * normal_vector[0]
        square1.vy -= impulse * normal_vector[1]
        square2.vx += impulse * normal_vector[0]
        square2.vy += impulse * normal_vector[1]

        # Small offset to separate the squares
        overlap = 0.5 * (distance - square1.side_length / 2 - square2.side_length / 2)
        square1.x -= overlap * normal_vector[0]
        square1.y -= overlap * normal_vector[1]
        square2.x += overlap * normal_vector[0]
        square2.y += overlap * normal_vector[1]

        # Play collision sound
        channel = play_collision_sound()
        if channel:
            global current_sound_index
            channel.play(collision_sounds[current_sound_index])
            current_sound_index = (current_sound_index + 1) % len(collision_sounds)

def line_intersect(p1, p2, v1, v2):
    """Check if line segments p1-p2 and v1-v2 intersect."""
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    return ccw(p1, v1, v2) != ccw(p2, v1, v2) and ccw(p1, p2, v1) != ccw(p1, p2, v2)

# Main game loop
running = True
paused = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    if not paused:
        update_trails()
        handle_square_collision(square1, square2)
        for square in squares:
            square.vy += gravity  # Apply gravity to vertical velocity
            handle_wall_collision(square)  # Check and handle collisions with window walls
            handle_polygon_collision(square, left_rhombus)  # Check and handle collisions with left rhombus
            handle_polygon_collision(square, right_rhombus)  # Check and handle collisions with right rhombus
            square.x += square.vx  # Update horizontal position
            square.y += square.vy  # Update vertical position
            square.angle += square.angular_velocity  # Update the angle of the square
            square.angular_velocity *= 0.99  # Dampen the rotational velocity
            # square.hue = (square.hue + 2) % 360  # Update hue for color change effect
            # square.color = hsv_to_rgb(square.hue / 360, 1.0, 1.0)  # Update square color

    # Clear the screen
    screen.fill(black)

    # Draw trails
    for square in squares:
        for i, pos in enumerate(square.trail):
            fade_power = 5.5
            alpha = int(255 * ((i / len(square.trail)) ** fade_power))
            trail_color = (*pos[2], alpha)
            trail_surface = pygame.Surface((pos[4], pos[4]), pygame.SRCALPHA)
            vertices = [(x - pos[0] + pos[4] // 2, y - pos[1] + pos[4] // 2) for x, y in pos[3]]
            pygame.draw.polygon(trail_surface, trail_color, vertices)
            pygame.draw.polygon(trail_surface, black, vertices, 1)  # Draw the black outline
            screen.blit(trail_surface, (pos[0] - pos[4] // 2, pos[1] - pos[4] // 2))

    # Draw polygons (chevron shapes)
    pygame.draw.polygon(screen, white, left_rhombus)
    pygame.draw.polygon(screen, white, right_rhombus)

    # Draw squares
    for square in squares:
        vertices = square.get_vertices()
        pygame.draw.polygon(screen, square.color, vertices)
        pygame.draw.polygon(screen, black, vertices, 3)  # Draw the black outline

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

    # Render text
    text_surface = font.render("Square Size: {}".format(square1.side_length / 2), True, pink)
    text_rect = text_surface.get_rect()
    text_rect.midbottom = (250, (height // 2) + 300)
    screen.blit(text_surface, text_rect)

    text_surface = font.render("Square Size: {}".format(square2.side_length / 2), True, green)
    text_rect = text_surface.get_rect()
    text_rect.midbottom = (850, (height // 2) + 300)
    screen.blit(text_surface, text_rect)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

pygame.quit()
sys.exit()