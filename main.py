import pygame, time, torch, math, cv2, pandas as pd, base64, os, numpy as np
from pygame.locals import *
from datetime import datetime
from djitellopy import Tello

# Initialize Pygame
pygame.init()

# Initialize Tello drone
tello = Tello()
print(torch.cuda.is_available())
print(torch.version.cuda)
print('__CUDA VERSION', )
# Set up a delay to ensure a stable connection
time.sleep(1)

# Set up the window
window_width, window_height = 500, 500
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Draw Drone Path")

# Set up colors
RED = (194, 24, 7)
BLUE = (0, 0, 255)
GREEN = (46, 139, 87)

# Set up the starting position
start_pos = [window_width // 2, window_height // 2]
start_pos2 = [window_width // 2, window_height // 2]  # new start position

# Set up variables for tracking path
path = []
draw_path = []
letter_path = []
drawing = False


# Set up the triangle coordinates
triangle_side_length = 10
half_triangle_side = triangle_side_length // 2
triangle_height = int(triangle_side_length * math.sqrt(3) / 2)
triangle_points = [
    (start_pos[0] - half_triangle_side, start_pos[1] + triangle_height),
    (start_pos[0], start_pos[1] - triangle_height),
    (start_pos[0] + half_triangle_side, start_pos[1] + triangle_height)
]

# Set up the triangle rotation angle
triangle_rotation = 0


# Set up variables for animation
animate_dot = False
dot_pos = list(start_pos)
start_pos2 = [window_width // 2, window_height // 2]

dot_speed = 2
dot_index = 0
green_dots = []
last_move_time = time.time()
last_move = []


"""
New triangle used to track
"""
# Set up the triangle coordinates
triangle_side_length2 = 10
half_triangle_side2 = triangle_side_length // 2
triangle_height2 = int(triangle_side_length * math.sqrt(3) / 2)
triangle_points2 = [
    (start_pos2[0] - half_triangle_side2, start_pos2[1] + triangle_height2),
    (start_pos2[0], start_pos2[1] - triangle_height2),
    (start_pos2[0] + half_triangle_side2, start_pos2[1] + triangle_height2)
]

# Set up the triangle rotation angle
triangle_rotation2 = 0

for_loop_finished = False
# Main loop
running = True

#Get exported data in folders
path_export = r"C:\Users\Theri\Escritorio\Drone_Github\images_from_dron"
export_path = r"C:\Users\Theri\Escritorio\Drone_Github\exported_data"

model = torch.hub.load(r'C:\Users\Theri\Escritorio\pathplanningdron\yolov5','custom',
                       path=r"C:\Users\Theri\Escritorio\pathplanningdron\best.pt", source = "local")  # load silently)

model.conf = 0.2 #NMS confidence threshold
model.iou = 0.7  # NMS IoU threshold
saved_data = []

def video_recorder():
    img_drone = tello.get_frame_read().frame
    img_drone = cv2.resize(img_drone, (416, 416))

    # modelo
    detect = model(img_drone)
    img_drone = np.squeeze(detect.render())  # bbox of detected objects

    for index, row in detect.pandas().xyxy[0].iterrows():  # iterate over the modelo output
        x1 = int(row["xmin"])
        y1 = int(row["ymin"])
        x2 = int(row["xmax"])
        y2 = int(row["ymax"])
        # center of BB
        x_center, y_center = ((x1 + x2) / 2, (y1 + y2) / 2)
        center_point = (x_center, y_center)

        name = str(row["name"])
        accuracy = float(round(row["confidence"], 4))
        timestamp = datetime.now()

        if accuracy >= 0.7:
                take_frame = tello.get_frame_read().frame
                take_frame = cv2.resize(take_frame, (416, 416))
                encoded_frame = base64.b64encode(
                    cv2.imencode('.jpg', take_frame)[1]).decode()  # formato para luego

                # poder visualizar las imagenes en el dataframe
                cv2.imwrite(os.path.join(path_export, f'{name}{accuracy}' + '.png'), take_frame)
                saved_data.append([x1, y1, x2, y2, center_point, name,
                                   accuracy, timestamp, encoded_frame])
    cv2.imshow("drone", img_drone)

    df = pd.DataFrame(columns=["Xmin", "Ymin", "Xmax", "Ymax", "box_center", "predict_name",
                               "accuracy", "date", "pitures", "coordenates"], data=saved_data)
    df.to_csv(os.path.join(export_path, 'data' + f'{timestamp.strftime("%m-%d-%Y")}' + '.csv'), encoding='utf-8',
              sep=",")


while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_RETURN:
                if len(path) > 0:
                    tello.connect()
                    #tello.takeoff()  # Set up a delay to ensure a stable connection
                    animate_dot = True
                    dot_index = 0
                    last_move_time = time.time()

            elif event.key == K_UP:
                start_pos[1] -= 10
                path.append(tuple(start_pos))
                letter_path.append('up')
            elif event.key == K_DOWN:
                start_pos[1] += 10
                path.append(tuple(start_pos))
                letter_path.append('down')
            elif event.key == K_LEFT:
                start_pos[0] -= 10
                path.append(tuple(start_pos))
                letter_path.append('left')
            elif event.key == K_RIGHT:
                start_pos[0] += 10
                path.append(tuple(start_pos))
                letter_path.append('right')
            elif event.key == K_a:
                triangle_rotation -= 90
                green_dots.append(tuple(start_pos))
                letter_path.append('a')
            elif event.key == K_d:
                triangle_rotation += 90
                green_dots.append(tuple(start_pos))
                letter_path.append('d')
            #Other options
            elif event.key == K_r:
                path = []  # Reset the path
                green_dots = []  # Reset dots
                letter_path = []  # Reset letters
                draw_path = []  # Reset blue path
                start_pos = [window_width // 2, window_height // 2]
                start_pos2 = start_pos
            elif event.key == K_q:  # Abort mission
                #tello.land()
                print("abort")

    # Update the triangle coordinates based on the new start_pos
    triangle_points = [
        (start_pos[0], start_pos[1] - half_triangle_side),
        (start_pos[0] - half_triangle_side, start_pos[1] + half_triangle_side),
        (start_pos[0] + half_triangle_side, start_pos[1] + half_triangle_side)
    ]
    # Rotate the triangle
    rotated_points = []
    for point in triangle_points:
        rotated_x = (point[0] - start_pos[0]) * math.cos(math.radians(triangle_rotation)) - (
                    point[1] - start_pos[1]) * math.sin(math.radians(triangle_rotation)) + start_pos[0]
        rotated_y = (point[0] - start_pos[0]) * math.sin(math.radians(triangle_rotation)) + (
                    point[1] - start_pos[1]) * math.cos(math.radians(triangle_rotation)) + start_pos[1]
        rotated_points.append((rotated_x, rotated_y))
    triangle_points = rotated_points

    # Draw the window
    window.fill((220, 220, 220))
    pygame.draw.polygon(window, RED, triangle_points, 0)

    for dot in green_dots:
        pygame.draw.circle(window, GREEN, dot, 5)

    # Draw the path
    if len(path) >= 2:
        pygame.draw.lines(window, RED, False, path, 5)

    # Animate the dron path along the red path
    if animate_dot:
        """
        To track the path I pass the given instructions that I have append before
        Start moving dron automatically
        """
        if dot_index < len(letter_path):
            video_recorder()
            l = letter_path[dot_index]
            if l == 'up':
                #tello.move_forward(40)
                time.sleep(.2)
                start_pos2[1] -= 10
                draw_path.append(tuple(start_pos2))
                print("UP")
            elif l == 'down':
                #tello.move_back(40)
                start_pos2[1] += 10
                draw_path.append(tuple(start_pos2))
                time.sleep(.2)
                print("donw")
            elif l == 'left':
                #tello.move_forward(40)
                start_pos2[0] -= 10
                draw_path.append(tuple(start_pos2))
                time.sleep(.5)
                print("left")
            elif l == 'right':
                #tello.move_forward(40)
                start_pos2[0] += 10
                draw_path.append(tuple(start_pos2))
                time.sleep(.2)
                print("right")

            elif l == 'a':
                triangle_rotation2 -= 90
                #tello.rotate_clockwise(-90)
                time.sleep(.2)
            elif l == 'd':
                triangle_rotation2 += 90
                #tello.rotate_clockwise(90)
                time.sleep(.2)
            dot_index +=1

            # Update the triangle coordinates based on the new start_pos
            triangle_points2 = [
                (start_pos2[0], start_pos2[1] - half_triangle_side2),
                (start_pos2[0] - half_triangle_side2, start_pos2[1] + half_triangle_side2),
                (start_pos2[0] + half_triangle_side2, start_pos2[1] + half_triangle_side2)
            ]
            # Rotate the triangle
            rotated_points2 = []

            for point in triangle_points2:
                rotated_x = (point[0] - start_pos2[0]) * math.cos(math.radians(triangle_rotation2)) - (
                        point[1] - start_pos2[1]) * math.sin(math.radians(triangle_rotation2)) + start_pos2[0]

                rotated_y = (point[0] - start_pos2[0]) * math.sin(math.radians(triangle_rotation2)) + (
                        point[1] - start_pos2[1]) * math.cos(math.radians(triangle_rotation2)) + start_pos2[1]
                rotated_points2.append((rotated_x, rotated_y))
            triangle_points2 = rotated_points2
            pygame.draw.polygon(window, BLUE, triangle_points2, 0)

    # Draw the path
    if len(draw_path) >= 2:
        pygame.draw.lines(window, BLUE, False, draw_path, 5)

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()

# Disconnect from the Tello drone
tello.disconnect()