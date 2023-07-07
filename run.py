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

# Calculate the valid range for circle spawning
spawn_range_x = screen.get_width() - circle_radius * 2
spawn_range_y = screen.get_height() - circle_radius * 2

# List of circle positions, their destinations, and their colors
circle_positions = [pygame.Vector2(random.randint(circle_radius, spawn_range_x), random.randint(circle_radius, spawn_range_y)) for _ in range(num_circles)]
circle_destinations = list(circle_positions)  # Start destinations as the initial positions
circle_colors = [random.choice(['red', 'blue', 'green']) for _ in range(num_circles)]  # Assign random colors

# Speed of the circles
speed = 2000

# Variable to store which circle is currently being controlled
current_circle = None
dragging = False

# Action point variable
action_points = 5  # Set the desired number of action points

def is_point_in_circle(point, circle_center, circle_radius):
    return (point - circle_center).length() <= circle_radius

def circles_collide(circle1_pos, circle2_pos):
    return (circle1_pos - circle2_pos).length() < min_distance

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

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
            if current_circle is not None and action_points > 0:
                action_points -= 1

        elif event.type == pygame.MOUSEMOTION:
            if dragging and current_circle is not None:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                # Constrain the mouse position within the screen boundaries
                constrained_pos = pygame.Vector2(
                    clamp(mouse_pos.x, circle_radius, screen.get_width() - circle_radius),
                    clamp(mouse_pos.y, circle_radius, screen.get_height() - circle_radius)
                )
                circle_destinations[current_circle] = constrained_pos

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
        
    if action_points == 0:
        message = font.render("You are out of moves!", True, pygame.Color("white"))
        message_rect = message.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(message, message_rect)

    # Display action points
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Actions: {action_points}", True, pygame.Color("white"))
    screen.blit(text, (10, 10))

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
