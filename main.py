from djitellopy import Tello
from pygame.locals import *
import pygame, time, torch, math, cv2, pandas as pd, base64, os, numpy as np

from datetime import datetime

# Speed of the drone
S = 60
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
FPS = 120

# Init pygame
pygame.init()

# Set up the window
window_width, window_height = 500, 500
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Draw Drone Path")

# Init Tello object that interacts with the Tello drone
tello = Tello()

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
last_move_time = time.time()
last_move = []

# Drone velocities between -100~100
for_back_velocity = 0
left_right_velocity = 0
up_down_velocity = 0
yaw_velocity = 0
speed = 10

# Set triangle to track
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

send_rc_control = False

# create update timer
pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

# Get exported data in folders
path_export = r"C:\Users\Theri\Escritorio\Drone_Github\images_from_dron"
export_path = r"C:\Users\Theri\Escritorio\Drone_Github\exported_data"

# Custom YOLOv5 model
model = torch.hub.load(r'C:\Users\Theri\Escritorio\pathplanningdron\yolov5', 'custom',
                       path=r"C:\Users\Theri\Escritorio\pathplanningdron\best.pt", source="local")  # load silently)

model.conf = 0.2  # NMS confidence threshold
model.iou = 0.7  # NMS IoU threshold
saved_data = []

tello.is_flying
def run():
    global for_back_velocity, left_right_velocity, up_down_velocity, yaw_velocity, send_rc_control

    tello.connect()
    tello.set_speed(speed)  # <-- set speed 10cm/s

    # In case streaming is on. This happens when we quit this program without the escape key.
    tello.streamoff()

    tello.streamon()

    frame_read = tello.get_frame_read()

    should_stop = False
    while not should_stop:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                update()
            elif event.type == pygame.QUIT:
                should_stop = True
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    should_stop = True
                else:
                    keydown(event.key)
            elif event.type == pygame.KEYUP:
                keyup(event.key)

        if frame_read.stopped:
            break

        draw(path)

        frame = frame_read.frame
        # model
        detect = model(frame)
        frame = np.squeeze(detect.render())  # bbox of detected objects

        # battery n.
        # text = "Battery: {}%".format(tello.get_battery())
        # cv2.putText(frame, text, (5, 720 - 5),
        #    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # frame = np.rot90(frame)
        # frame = np.flipud(frame)

        cv2.imshow("YOLOv5", frame)
        # frame = pygame.surfarray.make_surface(frame)

        # Draw the window
        pygame.display.update()

        time.sleep(1 / FPS)

    # Call it always before finishing. To deallocate resources.
    tello.end()


def keydown(key):
    global for_back_velocity, left_right_velocity, up_down_velocity, yaw_velocity

    """ Update velocities based on key pressed
    Arguments:
        key: pygame key
    """
    if key == pygame.K_UP:  # set forward velocity
        for_back_velocity = S
        start_pos[1] -= 10
        draw(path.append(tuple(start_pos)))
        store_letter('up')
    elif key == pygame.K_DOWN:  # set backward velocity
        for_back_velocity = -S
        start_pos[1] += 10
        draw(path.append(tuple(start_pos)))
        store_letter('down')
    elif key == pygame.K_LEFT:  # set left velocity
        left_right_velocity = -S
        start_pos[0] -= 10
        draw(path.append(tuple(start_pos)))
        store_letter('left')
    elif key == pygame.K_RIGHT:  # set right velocity
        left_right_velocity = S
        start_pos[0] += 10
        draw(path.append(tuple(start_pos)))
        store_letter('right')
    elif key == pygame.K_w:  # set up velocity
        up_down_velocity = S
    elif key == pygame.K_s:  # set down velocity
        up_down_velocity = -S
    elif key == pygame.K_a:  # set yaw clockwise velocity
        yaw_velocity = -S
        store_letter('rotleft')
    elif key == pygame.K_d:  # set yaw clockwise velocity
        yaw_velocity = S

        store_letter('rotright')

def keyup(key):
    global for_back_velocity, left_right_velocity, up_down_velocity, yaw_velocity, send_rc_control

    """ Update velocities based on key released
    Arguments:
        key: pygame key
    """
    if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
        for_back_velocity = 0
        store_letter('stop')
    elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
        left_right_velocity = 0
        store_letter('stop')
    elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
        up_down_velocity = 0

    elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
        yaw_velocity = 0

    elif key == pygame.K_t:  # takeoff
        tello.takeoff()
        send_rc_control = True

    elif key == pygame.K_l:  # land
        tello.land()
        send_rc_control = False


def draw(paths: list) -> None:
    """
    :param paths: list
    :return: None
    Draw canvas when the dron is not flying
    """
    global send_rc_control, path, start_pos
    if send_rc_control == True:
        if len(path) >= 2:
            window.fill([220, 220, 220])
            pygame.draw.lines(window, RED, False, path, 5)


def store_letter(letter: str) -> str:
    letter_path.append(letter)


def update():
    global for_back_velocity, left_right_velocity, up_down_velocity, yaw_velocity, send_rc_control

    if send_rc_control:
        tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)



run()
