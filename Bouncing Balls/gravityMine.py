import pygame

# Initialize Pygame
pygame.init()

# Screen Initializations
WIDTH, HEIGHT = 607, 1080
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("3 Second Ball Simulation")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Time Properties
fps = 60
timer = pygame.time.Clock()

# Ball Properties
ball_radius = 20
ball1 = {'x': 253.5, 'y': 500, 'vx': 5, 'vy': 2, 'color': white}
ball2 = {'x': 353.5, 'y': 500, 'vx': -5, 'vy': -2, 'color': white}

# Outer Circle Properties
circle_center = (WIDTH // 2, HEIGHT // 2)
circle_radius = 275
circle_thickness = 2



# -------------------------------------------------------------
# BALLS CLASS
# -------------------------------------------------------------
class Ball:
    def __init__(self, x_pos, y_pos, radius, color, mass, retention, y_speed, x_speed, id):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.color = color
        self.mass = mass
        self.retention = retention
        self.y_speed = y_speed
        self.x_speed = x_speed
        self.id = id
        self.circle = ''
    
    def draw(self):
        self.circle = pygame.draw.circle(screen, self.color, (self.x_pos, self.y_pos), self.radius)

    def check_gravity(self):
        if self.y_pos < 

ball1 = Ball(253.5, 500, 20, white, 100, 1.0, 5, 2, 1)
ball2 = Ball(353.5, 500, 20, white, 100, 1.0, 5, 2, 2)

# -------------------------------------------------------------
# MAIN GAME LOOP
# -------------------------------------------------------------
run = True
while run:
    timer.tick(fps)
    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Draw the large circle in the middle
    pygame.draw.circle(screen, 'white', circle_center, circle_radius, circle_thickness)

    ball1.draw()
    ball2.draw()

    pygame.display.flip()
pygame.quit()