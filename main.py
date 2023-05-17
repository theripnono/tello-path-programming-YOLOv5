import pygame
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Set up the window
window_width, window_height = 500, 500
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Draw Path")

# Set up colors
RED = (255, 0, 0)

# Set up the starting position
start_pos = [window_width // 2, window_height // 2]

# Set up variables for tracking path
path = []
drawing = False

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_RETURN:
                for coord in path:
                    print(coord)
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

    # Draw the window and circle
    window.fill((255, 255, 255))
    pygame.draw.circle(window, RED, start_pos, 5)

    # Draw the path
    if len(path) >= 2:
        pygame.draw.lines(window, RED, False, path, 2)

    # Update the display
    pygame.display.update()

# Print the path coordinates
print("Path coordinates:")
for coord in path:
    print(coord)

# Quit Pygame
pygame.quit()
