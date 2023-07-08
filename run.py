# CURRENT WORKING VERSION 
import pygame
import random
from sklearn.cluster import KMeans
import math
import shelve
import numpy as np
import matplotlib.pyplot as plt

pygame.init()
screen_height = 720
screen_width = 1280
circle_scale = 1
level = 0
speed = 2000  # Speed of the circles
is_playing_sound = False
track_selected = False
color_counts = {'red': 0, 'blue': 0, 'green': 0}

easy_mode = True
mesh_step = 100


starting_action_points = 5
init_circles = 5  # Circles on start
circle_radius = 40  # Circle radius and minimum distance between circles

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

running = True
dt = 0
# Define start screen state
game_state = "start_menu"
game_over = False
action_points = starting_action_points  # Set the desired number of action points
num_circles = init_circles
score = 0


def get_high_scores():
    try:
        f = shelve.open('high_scores.txt')
        scores = f['scores']
        scores.sort()
        while len(scores) < 5:
            scores.append(0)
        f.close()
        return scores 
    except:
        return [0] * 5

def write_high_score(new_score):
    f = shelve.open('high_scores.txt')
    try:
        old_scores = f['scores']
        if new_score not in old_scores:
            old_scores.append(new_score)
        old_scores.sort(reverse=True)
        new_scores = old_scores[0:5]
    except:
        new_scores = [new_score, 0, 0, 0, 0]

    f['scores'] = new_scores
    f.close()
    if new_score in new_scores:
        return True
    return False


# Load on click sounds
on_click_sounds = list()
for i in range(1, 10):
    on_click_sounds.append(pygame.mixer.Sound("sounds/clicks/space shield sounds - {}.wav".format(i)))

level_up_music = pygame.mixer.Sound("sounds/level_up.wav")


# Load level music
level_music = {
    0 : 'sounds/levels/WheresMySpaceship.wav',
    1 : 'sounds/levels/SpaceTheme.wav',
    2 : 'sounds/levels/FallingStars.wav',
    3 : 'sounds/levels/ThroughSpace.wav',
    4 : 'sounds/levels/Planetrise.wav',
    5 : 'sounds/levels/FrozenJam.wav',
    6 : 'sounds/levels/SpaceSprinkles.mp3',
    7 : 'sounds/levels/TowerDefenseTheme.mp3',
    8 : 'sounds/levels/HangInThere.mp3',
    9 : 'sounds/levels/MagicSpace.mp3',
}


# Twice the radius to prevent overlapping
min_distance = circle_radius * 2  

# Calculate the valid range for circle spawning
spawn_range_x = screen.get_width() - circle_radius * 2
spawn_range_y = screen.get_height() - circle_radius * 2

def normal_distribution(x, mean=0, standard_deviation=1):
    """Return the value of the normal distribution function at x."""
    return 1 / (standard_deviation * (2 * math.pi) ** 0.5) * math.exp(-0.5 * ((x - mean) / standard_deviation) ** 2)

def pick_color():
    """Pick a color with probability proportional to the negative of its count."""
    global color_counts
    
    # Compute scores for each color
    total_count = sum(color_counts.values())
    color_scores = {color: normal_distribution(count / total_count if total_count else 0) for color, count in color_counts.items()}

    # Pick color with highest score
    selected_color = max(color_scores, key=color_scores.get)
    
    # Update color count
    color_counts[selected_color] += 1
    
    return selected_color

# List of circle positions, their destinations, and their colors
circle_positions = [pygame.Vector2(random.randint(circle_radius, spawn_range_x), random.randint(circle_radius, spawn_range_y)) for _ in range(num_circles)]
circle_destinations = list(circle_positions)  # Start destinations as the initial positions
circle_colors = [(pick_color()) for _ in range(num_circles)]  # Assign random colors

# Variable to store which circle is currently being controlled
current_circle = None
dragging = False


def is_point_in_circle(point, circle_center, circle_radius):
    return (point - circle_center).length() <= circle_radius

def circles_collide(circle1_pos, circle2_pos):
    return (circle1_pos - circle2_pos).length() < min_distance

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def restart_game():
    global circle_positions, circle_destinations, circle_colors, action_points, circle_scale, num_circles, score, spawn_range_x, spawn_range_y
    num_circles = init_circles
    circle_positions = [pygame.Vector2(random.randint(circle_radius, spawn_range_x), random.randint(circle_radius, spawn_range_y)) for _ in range(num_circles)]
    circle_destinations = list(circle_positions)
    circle_colors = [(pick_color()) for _ in range(num_circles)]
    action_points = starting_action_points
    score = 0
    circle_scale = 1  # Reset circle_scale to 1
    spawn_range_x = screen.get_width() - circle_radius * 2
    spawn_range_y = screen.get_height() - circle_radius * 2
    min_distance = circle_radius * 2  # Twice the radius to prevent overlapping

    
def draw_start_screen():
    global is_playing_sound
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('arial', 40)
    title = font.render('Hugging Face Game Jam', True, (255, 255, 255))
    start_button = font.render('Press Space to Start', True, (255, 255, 255))
    screen.blit(title, (screen_width/2 - title.get_width()/2, screen_height/2 - title.get_height()/2))
    screen.blit(start_button, (screen_width/2 - start_button.get_width()/2, screen_height/2 + start_button.get_height()/2))
    
    if not is_playing_sound:
        pygame.mixer.music.load('sounds/start_menu.wav')
        pygame.mixer.music.play(-1)
        is_playing_sound = True

    pygame.display.update()

def draw_game_over_screen():
   global is_playing_sound
   screen.fill((0, 0, 0))
   font = pygame.font.SysFont('arial', 40)
   title = font.render('Game Over', True, (255, 255, 255))
   restart_button = font.render('R - Restart', True, (255, 255, 255))
   quit_button = font.render('Q - Quit', True, (255, 255, 255))
   screen.blit(title, (screen_width/2 - title.get_width()/2, screen_height/2 - title.get_height()/3))
   screen.blit(restart_button, (screen_width/2 - restart_button.get_width()/2, screen_height/1.9 + restart_button.get_height()))
   screen.blit(quit_button, (screen_width/2 - quit_button.get_width()/2, screen_height/2 + quit_button.get_height()/2))

   if not is_playing_sound:
       pygame.mixer.music.load('sounds/end_game.wav')
       pygame.mixer.music.play(-1)
       is_playing_sound = True

   pygame.display.update()

easy_lines = list()
def calculate_easy_mode(kmeans_model):
    global screen_width, screen_height, mesh_step, easy_lines
    # Initialize background mesh and predict
    xx, yy = np.meshgrid(np.arange(0, screen_width, mesh_step),
                         np.arange(0, screen_height, mesh_step))
    Z = kmeans_model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    easy_colors = ['gold', 'violet', 'cyan']

    # Contour over the mesh and extract coordinates
    cs = plt.contour(xx, yy, Z)

    lines = list()
    for item in cs.collections:
       for i in item.get_paths():
          v = i.vertices
          x = v[:, 0]
          y = v[:, 1]
          lines.append(list(zip([float(j) for j in x], [float(k) for k in y])))

    easy_lines = lines


def draw_easy_mode():
    global easy_lines, screen

    for i, line in enumerate(easy_lines):
        pygame.draw.lines(screen, color='gold', closed=False, points=line)  



def is_solved():
    kmeans = KMeans(n_clusters=3, n_init=10)  # Change the number of clusters as needed
    kmeans.fit([list(circle_positions[i]) for i in range(num_circles)])

    if easy_mode:
        calculate_easy_mode(kmeans)

    # Check if each cluster contains circles of the same color
    cluster_colors_match = True
    for cluster_label in range(3):  # Assuming 3 clusters for this example
        cluster_indices = [i for i in range(num_circles) if kmeans.labels_[i] == cluster_label]
        cluster_colors_set = set([circle_colors[i] for i in cluster_indices])
        if len(cluster_colors_set) > 1:
            cluster_colors_match = False
            break

    return cluster_colors_match

def move_circles():
    global num_circles, circle_positions, circle_destinations, dt
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

def level_up():
    global circle_scale, level, level_music, level_up_music, is_playing_sound, num_circles, circle_positions, circle_destinations, circle_colors, action_points, score

    circle_scale *= 0.7  # Set circle_scale to 0.5 if is_solved is True
    level += 1
    score += action_points * 100 + 1000

    old_scaling = .5

    origin = (screen_width * .5, screen_height * .5)

    # Compress old points
    for i in range(len(circle_positions)):
        old_x, old_y = circle_positions[i]
        relative_x = old_x - origin[0]
        relative_y = old_y - origin[1]
        new_x = relative_x * old_scaling + origin[0]
        new_y = relative_y * old_scaling + origin[1]
        circle_destinations[i] = pygame.Vector2(new_x, new_y)

    move_circles()


    # Adding 12 more circles to the game
    for _ in range(3):
        # one anywhere to the left of center
        circle_positions.append(pygame.Vector2(random.randint(circle_radius, int(origin[0] * old_scaling)), random.randint(circle_radius, spawn_range_y)))
        circle_destinations.append(circle_positions[-1])
        circle_colors.append(pick_color())

        # one anywhere to the right of center
        circle_positions.append(pygame.Vector2(random.randint(int(origin[0] * (1 + old_scaling)), spawn_range_x), random.randint(circle_radius, spawn_range_y)))
        circle_destinations.append(circle_positions[-1])
        circle_colors.append(pick_color())

        # One anywhere above center
        circle_positions.append(pygame.Vector2(random.randint(circle_radius, spawn_range_x), random.randint(circle_radius, int(origin[1] * old_scaling))))
        circle_destinations.append(circle_positions[-1])
        circle_colors.append(pick_color())    

        # One anywhere below center
        circle_positions.append(pygame.Vector2(random.randint(circle_radius, spawn_range_x), random.randint(int(origin[1] * (1 + old_scaling)), spawn_range_y)))
        circle_destinations.append(circle_positions[-1])
        circle_colors.append(pick_color())      
    num_circles += 12


    # Increase action_points by 6
    action_points += 8

    # Stop music, play level-up, start new level music
    pygame.mixer.music.stop()
    pygame.mixer.Sound.play(level_up_music)
    pygame.mixer.Sound.fadeout(level_up_music, 500)
    if level > 8:
        pygame.mixer.music.load(level_music[9])
    else:
        pygame.mixer.music.load(level_music[level])

    pygame.mixer.music.play(-1)
    is_playing_sound = False



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

                    # Pick a sound and play it
                    music_idx = i % 9 
                    pygame.mixer.Sound.play(on_click_sounds[music_idx])

                    break  # Stop checking after a circle is found
                current_circle = None
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            if current_circle is not None and action_points > 0:
                action_points -= 1

                if is_solved():
                    level_up()

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
            pygame.mixer.music.stop()
            pygame.mixer.music.load(level_music[0])
            pygame.mixer.music.play(-1)
            is_playing_sound = True
            restart_game()
            game_over = False

    if game_over:
        draw_game_over_screen()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = "start_menu"
            game_over = False
            score = 0
            action_points = starting_action_points
        if keys[pygame.K_q]:
            pygame.quit()
            quit()

    elif game_state == "game":

        screen.fill("black")

        move_circles()

        if easy_mode and easy_lines:
            draw_easy_mode()

        # Draw all circles with their assigned colors
        for i in range(num_circles):
            scaled_radius = int(circle_radius * circle_scale)
            pygame.draw.circle(screen, circle_colors[i], circle_positions[i], scaled_radius)
            min_distance = circle_radius * 2 * circle_scale 
            
        if action_points == 0:
            game_over = True

        # Display action points
        font = pygame.font.SysFont(None, 36)
        ap_text = font.render(f"Actions: {action_points}", True, pygame.Color("white"))
        screen.blit(ap_text, (10, 10))

        # Display Score
        score_text = font.render(f"Score: {score}", True, pygame.Color("white"))
        screen.blit(score_text, (1000, 10))

        pygame.display.flip()

        dt = clock.tick(60) / 1000
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            restart_game()

pygame.quit()
