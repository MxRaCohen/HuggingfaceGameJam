import pygame
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# Number of circles
num_circles = 20

# List of circle positions, their destinations, and their colors
circle_positions = [pygame.Vector2(random.randint(0, screen.get_width()), random.randint(0, screen.get_height())) for _ in range(num_circles)]
circle_destinations = list(circle_positions)  # Start destinations as the initial positions
circle_colors = [random.choice(['red', 'blue', 'green']) for _ in range(num_circles)]  # Assign random colors

# Speed of the circles
speed = 300

# variable to store which circle is currently being controlled
current_circle = 0

def is_point_in_circle(point, circle_center, circle_radius):
    return (point-circle_center).length() <= circle_radius

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = pygame.Vector2(pygame.mouse.get_pos())

            for i in range(num_circles):
                if is_point_in_circle(click_pos, circle_positions[i], 40):
                    current_circle = i
                    break  # Stop checking after a circle is found
            else:
                # If the click wasn't on a circle, set the clicked position as the destination
                circle_destinations[current_circle] = click_pos

    screen.fill("black")

    # Draw all circles with their assigned colors
    for i in range(num_circles):
        pygame.draw.circle(screen, circle_colors[i], circle_positions[i], 40)

    # Move all circles towards their destinations
    for i in range(num_circles):
        if circle_positions[i] != circle_destinations[i]:
            direction = (circle_destinations[i] - circle_positions[i]).normalize()
            if (circle_destinations[i] - circle_positions[i]).length() <= speed * dt:
                circle_positions[i] = circle_destinations[i]
            else:
                circle_positions[i] += direction * speed * dt

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
