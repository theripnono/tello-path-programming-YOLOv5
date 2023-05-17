import pygame
import time
from pygame.locals import *
from djitellopy import Tello

# Initialize Pygame
pygame.init()

# Initialize Tello drone
tello = Tello()


# Set up a delay to ensure a stable connection
time.sleep(2)
# Set up the window
window_width, window_height = 500, 500
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Draw Path")

# Set up colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set up the starting position
start_pos = [window_width // 2, window_height // 2]

# Set up variables for tracking path
path = []
drawing = False

# Set up variables for animation
animate_dot = False
dot_pos = list(start_pos)
dot_speed = 2
dot_index = 0
last_move_time = time.time()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_RETURN:
                if len(path) > 0:
                    animate_dot = True
                    dot_index = 0
                    last_move_time = time.time()

                    tello.connect()
                    # Set up a delay to ensure a stable connection
                    time.sleep(2)
                    tello.takeoff()
            elif event.key == K_a:
                start_pos[0] -= 10
                path.append(tuple(start_pos))
            elif event.key == K_d:
                start_pos[0] += 10
                path.append(tuple(start_pos))
            elif event.key == K_w:
                start_pos[1] -= 10
                path.append(tuple(start_pos))
            elif event.key == K_s:
                start_pos[1] += 10
                path.append(tuple(start_pos))
            elif event.key == K_q:
                tello.land()

    # Draw the window and circle
    window.fill((255, 255, 255))
    pygame.draw.circle(window, RED, start_pos, 5)

    # Draw the path
    if len(path) >= 2:
        pygame.draw.lines(window, RED, False, path, 2)

    # Animate the dot along the path
    if animate_dot:
        if dot_index < len(path):
            if time.time() - last_move_time >= .1:
                target_pos = path[dot_index]
                direction = [target_pos[0] - dot_pos[0], target_pos[1] - dot_pos[1]]
                length = pygame.math.Vector2(direction).length()
                normalized_direction = [direction[0] / length, direction[1] / length]
                dot_pos[0] += normalized_direction[0] * dot_speed
                dot_pos[1] += normalized_direction[1] * dot_speed

                if pygame.math.Vector2(target_pos).distance_to(pygame.math.Vector2(dot_pos)) < dot_speed:
                    dot_pos = list(target_pos)
                    dot_index += 1
                    print(dot_index,dot_pos)
                    # Move the Tello drone based on the dot's position
                    tello.move_forward(20)
                    time.sleep(0.5)
                    # Adjust the distance as needed
                    print("TELLO SE MUEVE")
                last_move_time = time.time()

        pygame.draw.circle(window, BLUE, dot_pos, 3)

    # Update the displayQ
    pygame.display.update()

# Print the path coordinates
print("Path coordinates:")
for coord in path:
    print(coord)

# Quit Pygame
pygame.quit()

# Disconnect from the Tello drone
tello.disconnect()