import pygame
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# Number of circles
num_circles = 20

# Circle radius and minimum distance between circles
circle_radius = 40
min_distance = circle_radius * 2  # Twice the radius to prevent overlapping

# List of circle positions, their destinations, and their colors
circle_positions = [pygame.Vector2(random.randint(0, screen.get_width()), random.randint(0, screen.get_height())) for _ in range(num_circles)]
circle_destinations = list(circle_positions)  # Start destinations as the initial positions
circle_colors = [random.choice(['red', 'blue', 'green']) for _ in range(num_circles)]  # Assign random colors

# Speed of the circles
speed = 2000

# Variable to store which circle is currently being controlled
current_circle = None
dragging = False

def is_point_in_circle(point, circle_center, circle_radius):
    return (point - circle_center).length() <= circle_radius

def circles_collide(circle1_pos, circle2_pos):
    return (circle1_pos - circle2_pos).length() < min_distance

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = pygame.Vector2(pygame.mouse.get_pos())

            for i in range(num_circles):
                if is_point_in_circle(click_pos, circle_positions[i], circle_radius):
                    current_circle = i
                    dragging = True
                    break  # Stop checking after a circle is found

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging and current_circle is not None:
                circle_destinations[current_circle] = pygame.Vector2(pygame.mouse.get_pos())

    screen.fill("black")

    # Move all circles towards their destinations
    for i in range(num_circles):
        if circle_positions[i] != circle_destinations[i]:
            direction = (circle_destinations[i] - circle_positions[i]).normalize()
            if (circle_destinations[i] - circle_positions[i]).length() <= speed * dt:
                circle_positions[i] = circle_destinations[i]
            else:
                circle_positions[i] += direction * speed * dt

        # Check for collisions with other circles
        for j in range(num_circles):
            if i != j and circles_collide(circle_positions[i], circle_positions[j]):
                # Adjust the position of circle i if it collides with circle j
                displacement = (circle_positions[i] - circle_positions[j]).normalize() * min_distance
                circle_positions[i] = circle_positions[j] + displacement

    # Draw all circles with their assigned colors
    for i in range(num_circles):
        pygame.draw.circle(screen, circle_colors[i], circle_positions[i], circle_radius)

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
