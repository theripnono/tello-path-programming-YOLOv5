import pygame
from djitellopy import Tello

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
width, height = 50, 50
window_size = (width, height)

# Create the window
window = pygame.display.set_mode(window_size)

# Set the initial line start position
line_start = None

# Store the drawn paths
paths = []

# Define the key codes for drawing
draw_keys = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]

# Initialize the Tello drone
tello = Tello()

# Connect to the Tello drone
tello.connect()

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in draw_keys:
                # Set the line start position when the draw key is pressed
                line_start = pygame.mouse.get_pos()

        elif event.type == pygame.KEYUP:
            if event.key in draw_keys and line_start is not None:
                # Draw the line when the draw key is released
                line_end = pygame.mouse.get_pos()
                paths.append((line_start, line_end))
                line_start = None

    # Fill the window with a color (white in this case)
    window.fill((255, 255, 255))

    # Draw the stored paths
    for path in paths:
        pygame.draw.line(window, (0, 0, 0), path[0], path[1], 1)

    # Process the stored paths and send commands to the Tello drone
    for path in paths:
        start_pos, end_pos = path

        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]

        # Example drone movement commands
        if dx > 0:
            tello.move_right(100)
        elif dx < 0:
            tello.move_left(100)

        if dy > 0:
            tello.move_forward(100)
        elif dy < 0:
            tello.move_back(100)

        # Example rotation command
        tello.rotate_counter_clockwise(90)

        # Add additional commands based on your requirements

    # Update the display
    pygame.display.flip()

# Disconnect from the Tello drone
tello.disconnect()

# Quit Pygame
pygame.quit()