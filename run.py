# CURRENT WORKING VERSION 
import pygame
import random
from sklearn.cluster import KMeans

pygame.init()
screen_height = 720
screen_width = 1280

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
running = True
dt = 0
circle_scale = 1
# Define start screen state
game_state = "start_menu"
game_over = False

# Number of circles
num_circles = 5

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

def restart_game():
    global circle_positions, circle_destinations, circle_colors, action_points
    circle_positions = [pygame.Vector2(random.randint(circle_radius, spawn_range_x), random.randint(circle_radius, spawn_range_y)) for _ in range(num_circles)]
    circle_destinations = list(circle_positions)
    circle_colors = [random.choice(['red', 'blue', 'green']) for _ in range(num_circles)]
    action_points = 5

def draw_start_screen():
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('arial', 40)
    title = font.render('Hugging Face Game Jam', True, (255, 255, 255))
    start_button = font.render('Press Space to Start', True, (255, 255, 255))
    screen.blit(title, (screen_width/2 - title.get_width()/2, screen_height/2 - title.get_height()/2))
    screen.blit(start_button, (screen_width/2 - start_button.get_width()/2, screen_height/2 + start_button.get_height()/2))
    pygame.display.update()

def draw_game_over_screen():
   screen.fill((0, 0, 0))
   font = pygame.font.SysFont('arial', 40)
   title = font.render('Game Over', True, (255, 255, 255))
   restart_button = font.render('R - Restart', True, (255, 255, 255))
   quit_button = font.render('Q - Quit', True, (255, 255, 255))
   screen.blit(title, (screen_width/2 - title.get_width()/2, screen_height/2 - title.get_height()/3))
   screen.blit(restart_button, (screen_width/2 - restart_button.get_width()/2, screen_height/1.9 + restart_button.get_height()))
   screen.blit(quit_button, (screen_width/2 - quit_button.get_width()/2, screen_height/2 + quit_button.get_height()/2))
   pygame.display.update()

def is_solved():
    kmeans = KMeans(n_clusters=3)  # Change the number of clusters as needed
    kmeans.fit([list(circle_positions[i]) for i in range(num_circles)])

    # Check if each cluster contains circles of the same color
    cluster_colors_match = True
    for cluster_label in range(3):  # Assuming 3 clusters for this example
        cluster_indices = [i for i in range(num_circles) if kmeans.labels_[i] == cluster_label]
        cluster_colors_set = set([circle_colors[i] for i in cluster_indices])
        if len(cluster_colors_set) > 1:
            cluster_colors_match = False
            break

    return cluster_colors_match

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
                current_circle = None
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            if current_circle is not None and action_points > 0:
                action_points -= 1

                if is_solved():
                    circle_scale = 0.5  # Set circle_scale to 0.5 if is_solved is True

                    

        elif event.type == pygame.MOUSEMOTION:
            if dragging and current_circle is not None:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                # Constrain the mouse position within the screen boundaries
                constrained_pos = pygame.Vector2(
                    clamp(mouse_pos.x, circle_radius, screen.get_width() - circle_radius),
                    clamp(mouse_pos.y, circle_radius, screen.get_height() - circle_radius)
                )
                circle_destinations[current_circle] = constrained_pos

    if game_state == "start_menu":
        draw_start_screen()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = "game"
            restart_game()
            game_over = False

    if game_over:
        draw_game_over_screen()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = "start_menu"
            game_over = False
            action_points = 5
        if keys[pygame.K_q]:
            pygame.quit()
            quit()

    elif game_state == "game":

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
            scaled_radius = int(circle_radius * circle_scale)
            pygame.draw.circle(screen, circle_colors[i], circle_positions[i], scaled_radius)
            
        if action_points == 0:
            game_over = True

        # Display action points
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Actions: {action_points}", True, pygame.Color("white"))
        screen.blit(text, (10, 10))

        pygame.display.flip()

        dt = clock.tick(60) / 1000
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            restart_game()

pygame.quit()
