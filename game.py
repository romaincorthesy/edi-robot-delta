#!/usr/bin/env python3

import pygame
from pygame.locals import *
from time import time_ns, sleep
from math import sqrt
from enum import Enum
import json
import RPi.GPIO as GPIO

import ScaleConversion as SC
from InputDevice import Touchfoil, Mouse, IInputDevice
from OutputDevice import DeltaRobot

# GPIO definitions
USER_FOLLOWS_PANEL_PIN: int = 23
ROBOT_FOLLOWS_PANEL_PIN: int = 24
BUTTON_PIN: int = 18

# Color constants
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Screen setup
DISPLAY_WIDTH: int = 1440
DISPLAY_HEIGHT: int = 1440
USABLE_RADIUS: int = 450
DEBUG_SHOW_GRID: bool = False   # Set to True to display grid for motors limits

# User screen position setup
USER_DIFF_THRESHOLD: int = 1
user_x: int = 0
user_y: int = 0

# Robot screen position setup
robot_x: int = 0
robot_y: int = 0
FAKE_ROBOT_DELAY_MS: int = 100
last_time_ns: int = time_ns()

# Robot home z positions
Z_RETRACTED = -0.120
Z_WORKING = -0.150


# Duration of the modes
ROBOT_FOLLOWS_DURATION_MS: int = 20_000
USER_FOLLOWS_DURATION_MS: int = 20_000
mode_duration_last_time_ns: int = time_ns()

# If this flag is set to True, the game stays in the mode in wich it was started, useful for testing the modes.
# Running the game whith the -r, -u or -t flag will set it to True, running it whith no arg (expo mode) will set it to false.
FLAG_STAY_IN_FIRST_MODE: bool = False


class GameMode(Enum):
    IDLE_STATE = 0
    USER_FOLLOWS = 1
    ROBOT_FOLLOWS = 2
    TEST_CMD = 3


def drawText(text: str, topleft: tuple[int, int], color: tuple[int, int, int]):
    """Add a text on the screen. pygame.display.update() must be called after.

    Args:
        text (str): text to display
        topleft (tuple[int, int]): top left corner position
        color (tuple[int, int, int]): RVB description of a color
    """
    img = font.render(text, True, color)
    rect = img.get_rect()
    rect.topleft = topleft
    screen.blit(img, rect)


def updateScreen() -> None:
    """Update position text and dot according to current input device position
    """
    screen.fill(GRAY)

    if DEBUG_SHOW_GRID:
        for x, y, color in points:
            pygame.draw.circle(
                screen, color, (x, y), 2)

    drawText(f'Robot: {robot_x}, {robot_y}', (20, 50), RED)
    pygame.draw.circle(screen, RED, (robot_x, robot_y), 6)

    drawText(f'User: {user_x}, {user_y}', (20, 20), BLACK)
    pygame.draw.circle(screen, BLACK, (user_x, user_y), 3)

    # Input device radius
    pygame.draw.circle(screen, BLACK, (int(DISPLAY_WIDTH/2),
                                       int(DISPLAY_HEIGHT/2)), USABLE_RADIUS, 1)

    # Output device radius
    #! TODO : THIS DOESN'T WORK
    # work_radius = int(SC.remap(0, robot.operational_space.x_axis_max,
    #                   0, USABLE_RADIUS, robot.WORK_RADIUS))
    # print("work radius:", work_radius)
    # pygame.draw.circle(screen, RED, (int(DISPLAY_WIDTH/2),
    #                                  int(DISPLAY_HEIGHT/2)), work_radius, 1)

    if winner == "user":
        userWon()
    elif winner == "robot":
        robotWon()

    pygame.display.update()


# Input device
def updateCallback(device: IInputDevice) -> None:
    """Function called when the input device fires a event indicating a new position. Update user position.

    Args:
        device (IInputDevice): the input device which fired a event
    """
    global user_x, user_y, FLAG_SEND_POSITION_TO_ROBOT

    if game_mode == GameMode.USER_FOLLOWS:
        # Update user position asap
        user_x = device.x
        user_y = device.y
        FLAG_SEND_POSITION_TO_ROBOT = True
    elif game_mode == GameMode.ROBOT_FOLLOWS:
        # Only update user position if the input position has moved enough
        if abs(device.x - user_x) > USER_DIFF_THRESHOLD or abs(device.y - user_y) > USER_DIFF_THRESHOLD:
            user_x = device.x
            user_y = device.y
            FLAG_SEND_POSITION_TO_ROBOT = True


# input_device = Touchfoil(screen_height=DISPLAY_HEIGHT, screen_width=DISPLAY_WIDTH)
input_device = Mouse(screen_height=DISPLAY_HEIGHT, screen_width=DISPLAY_WIDTH,
                     screen_usable_height=2*USABLE_RADIUS, screen_usable_width=2*USABLE_RADIUS)
input_device.callbackUpdate = updateCallback


# Output device
robot = DeltaRobot(A_motor_id=0x11, B_motor_id=0x12, C_motor_id=0x13,
                   A_encoder_id=0x11, B_encoder_id=0x12, C_encoder_id=0x13,
                   sniff_traffic=False)


def screenToRobot(input_device: IInputDevice, robot: DeltaRobot, force_value: tuple[int, int] = None) -> tuple[float, float]:
    """Convert from screen to robot coordinate system. 

    Args:
        input_device (IInputDevice): an input device from which to convert the x and y properties.
        robot (DeltaRobot): a robot with an operational space to convert to.
        force_value (tuple[int, int], optional): an position to convert instead of the input device's position. Defaults to None.

    Returns:
        tuple[float, float]: a pair x,y in the robot's coordinate system
    """
    if force_value != None:
        x_in = force_value[0]
        y_in = force_value[1]
    else:
        x_in = input_device.x
        y_in = input_device.y

    start_screen_usable_x = (
        input_device.screen_width-input_device.screen_usable_width)/2
    end_screen_usable_x = start_screen_usable_x + input_device.screen_usable_width
    start_screen_usable_y = (
        input_device.screen_height-input_device.screen_usable_height)/2
    end_screen_usable_y = start_screen_usable_x + input_device.screen_usable_height
    x = SC.remap(start_screen_usable_x, end_screen_usable_x, robot.operational_space.x_axis_min,
                 robot.operational_space.x_axis_max, x_in)
    y = SC.remap(start_screen_usable_y, end_screen_usable_y, robot.operational_space.y_axis_min,
                 robot.operational_space.y_axis_max, y_in)

    return (x, y)


def robotToScreen(robot: DeltaRobot, input_device: IInputDevice) -> tuple[float, float]:
    """Convert from robot to screen coordinate system.

    Args:
        robot (DeltaRobot): a robot from which to convert the x and y properties
        input_device (IInputDevice): an input device with a screen width and height to convert to

    Returns:
        tuple[float, float]: a x,y pair in the screen space
    """
    x = SC.remap(robot.operational_space.x_axis_min,
                 robot.operational_space.x_axis_max, 0, input_device.screen_width, robot.x)
    y = SC.remap(robot.operational_space.y_axis_min,
                 robot.operational_space.y_axis_max, 0, input_device.screen_height, robot.y)

    return (x, y)


def isInsideRadius(x: int, y: int, radius: int, center_x: int, center_y: int) -> bool:
    dx = x - center_x
    dy = y - center_y
    point_radius = sqrt(dx**2 + dy**2)

    return point_radius < radius


def userWon() -> None:
    """Called when the user has outsped the robot"""
    drawText('Vous avez gagné !', (700, 450), BLACK)


def robotWon() -> None:
    """Called when the robot has outsped the user"""
    drawText('Vous avez perdu ! Vous êtes trop lent', (700, 450), BLACK)


def moveRobotToHome(z_pos: float):
    """Move the robot to center of screen and to the given z position

    Args:
        z_pos (float): z position of the base in mm
    """
    home_x, home_y = screenToRobot(input_device, robot, force_value=(
        DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2))
    robot.moveBaseToXYZ((home_x, home_y, z_pos))


def moveRobotToRetractedHome():
    """Move the robot to the center of the screen, in the retracted position (waiting position).
    """
    moveRobotToHome(Z_RETRACTED)


def moveRobotToWorkingHome():
    """Move the robot to the center of the screen near the glass (working starting position).
    """
    moveRobotToHome(Z_WORKING)


# Load robot movement path
path = []
with open("./path.json") as f:
    path = json.load(f)
    print("Path length: ", len(path))
path_scale_x: float = 0.6
path_scale_y: float = 1.0


def getPathPoint(path, i):
    return (int(path[i][0] * path_scale_x + DISPLAY_WIDTH // 2), int(path[i][1] * path_scale_y + DISPLAY_HEIGHT // 2))


if __name__ == "__main__":
    import sys

    # Get argument to set GameMode
    if len(sys.argv) > 1:   # sys.argv[0] : fileName
        arg = sys.argv[1]
    else:
        arg = None

    print(f"\nThis file ({sys.argv[0]}) can be optionnaly run with one of these flags:\n\
    -u, --user-follows  : try to follow the robot as fast as you can\n\
    -r, --robot-follows : try to outspeed the robot\n\
    -t, --test-cmd      : send commands to test that the robot is working as intended\n")

    if arg == "-u" or arg == "--user-follows":
        print("Running in user-follows mode: try to follow the robot as fast as you can\n")
        game_mode: GameMode = GameMode.USER_FOLLOWS
        FLAG_STAY_IN_FIRST_MODE = True
    elif arg == "-r" or arg == "--robot-follows":
        print("Running in robot-follows: try to outspeed the robot")
        game_mode: GameMode = GameMode.ROBOT_FOLLOWS
        FLAG_STAY_IN_FIRST_MODE = True
        FLAG_STAY_IN_FIRST_MODE = True
    elif arg == "-t" or arg == "--test-cmd":
        print("Running in test mode\n--------------------\nAvailable commands:\n\
    p - Position:   p0,0,-0.200  = moveBaseToXYZ(0, 0, -0.200) [m]\n\
    c - Center:     c-0.200      = moveBaseToXYZ(0, 0, -0.200) [m]\n\
    f - Flat plane: f0.010,0.020 = moveBaseToXYZ(0.010, 0.020, z_max) [m]\n\
    a - Angles:     a0,0,30      = moveAllAxesTo(0, 0, 30) [°]\n\
    z - Z axis:     z20          = moveAllAxesTo(20, 20, 20) [°]\n")
        game_mode: GameMode = GameMode.TEST_CMD
        FLAG_STAY_IN_FIRST_MODE = True
    else:
        print("Running without known args, standard use (expo)\n")
        FLAG_STAY_IN_FIRST_MODE = False
        game_mode: GameMode = GameMode.IDLE_STATE

    pygame.init()
    # If set_mode is raising "pygame.error: Unable to open a console terminal",
    # and the python file is launched through ssh, the reason is there is no DISPLAY set.
    # Run "export DISPLAY=:0" through ssh and try again.
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.toggle_fullscreen()
    font = pygame.font.SysFont(None, 24)

    FLAG_SEND_POSITION_TO_ROBOT = True
    DELTA_POSITION_WIN_LOOSE_THRESHOLD: int = 150
    winner = ""
    speed_delta_ns: int = 1_000_000
    dxy = 0.0
    i = 0

    # Flags to keep states init from running multiple times
    idle_state_init_done: bool = False
    robot_follows_state_init_done: bool = False
    user_follows_state_init_done: bool = False

    if DEBUG_SHOW_GRID:
        print("Calculating motors limits...")
        points: list[tuple[int, int, tuple[int, int, int]]] = []
        for x in range(0, DISPLAY_WIDTH, 4):
            for y in range(0, DISPLAY_HEIGHT, 4):
                x_r, y_r = screenToRobot(input_device, robot, (x, y))
                try:
                    angle_A, angle_B, angle_C = robot.IGM(
                        (x_r, y_r, robot.operational_space.z_axis_max))
                    points.append((int(x), int(y), GREEN))
                except ValueError:
                    points.append((int(x), int(y), RED))
        print("Done calculating. Everything's gonna be sloooow")

    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(ROBOT_FOLLOWS_PANEL_PIN, GPIO.OUT)
    GPIO.setup(USER_FOLLOWS_PANEL_PIN, GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Main loop
    running = True
    while running:
        # Check for events
        for event in pygame.event.get():
            # Windows closed with cross
            if event.type == pygame.QUIT:
                running = False

            # Quit the game with a press on Escape key
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            # Update device position on motion
            elif event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                input_device.updatePosition(x, y)

        # Update user-robot position error
        dx = user_x - robot_x
        dy = user_y - robot_y
        dxy = sqrt(dx*dx + dy*dy)

        if game_mode == GameMode.IDLE_STATE:
            if not idle_state_init_done:
                # This must be done only once when entering the state
                GPIO.output(USER_FOLLOWS_PANEL_PIN, GPIO.LOW)
                GPIO.output(ROBOT_FOLLOWS_PANEL_PIN, GPIO.LOW)

                moveRobotToWorkingHome()
                sleep(1)
                moveRobotToRetractedHome()
                idle_state_init_done = True

            # Wait for button to be pressed, then start go to ROBOT_FOLLOWS state
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                idle_state_init_done = False
                game_mode = GameMode.ROBOT_FOLLOWS

                # Start a timer for the duration of the ROBOT_FOLLOWS state
                mode_duration_last_time_ns = time_ns()

        elif game_mode == GameMode.ROBOT_FOLLOWS:
            if not robot_follows_state_init_done:
                # This must be done only once when entering the state
                GPIO.output(USER_FOLLOWS_PANEL_PIN, GPIO.LOW)
                GPIO.output(ROBOT_FOLLOWS_PANEL_PIN, GPIO.HIGH)

                sleep(1)
                moveRobotToWorkingHome()
                robot_follows_state_init_done = True

            if dxy > DELTA_POSITION_WIN_LOOSE_THRESHOLD:
                # User wins against robot
                winner = "user"

            # Send the new position to the robot
            if FLAG_SEND_POSITION_TO_ROBOT:
                FLAG_SEND_POSITION_TO_ROBOT = False

                x, y = screenToRobot(input_device, robot, (user_x, user_y))
                print(user_x, user_y, x, y)

                if isInsideRadius(user_x, user_y, USABLE_RADIUS, int(DISPLAY_WIDTH/2), int(DISPLAY_HEIGHT/2)):
                    if robot.moveBaseToXYZ((x, y, robot.operational_space.z_axis_max)) != 0:
                        print("Error sending message")
                else:
                    print("User position out of usable area")

            # Go to next mode (USER_FOLLOWS)
            if not FLAG_STAY_IN_FIRST_MODE and time_ns() - mode_duration_last_time_ns > USER_FOLLOWS_DURATION_MS*1_000_000:
                sleep(1)
                moveRobotToRetractedHome()
                sleep(2)
                robot_follows_state_init_done = False
                game_mode = GameMode.USER_FOLLOWS

                mode_duration_last_time_ns = time_ns()

        elif game_mode == GameMode.USER_FOLLOWS:
            if not robot_follows_state_init_done:
                # This must be done only once when entering the state
                GPIO.output(ROBOT_FOLLOWS_PANEL_PIN, GPIO.LOW)
                GPIO.output(USER_FOLLOWS_PANEL_PIN, GPIO.HIGH)

                i = 0

                sleep(1)
                moveRobotToWorkingHome()
                sleep(1)
                robot_follows_state_init_done = True

            if dxy > DELTA_POSITION_WIN_LOOSE_THRESHOLD:
                # Robot wins against user
                winner = "robot"

            if speed_delta_ns > 1_000:
                speed_delta_ns -= 10_000

            if time_ns() - last_time_ns > speed_delta_ns:

                print("Current delta_ms between points: ", speed_delta_ns/1000.0)

                robot_x, robot_y = getPathPoint(path, i)
                # print(f"New point: {robot_x}, {robot_y}")
                x, y = screenToRobot(input_device, robot, (robot_x, robot_y))
                if robot.moveBaseToXYZ((x, y, robot.operational_space.z_axis_max)) != 0:
                    print("Error sending message")

                i += 1
                i %= len(path)

                last_time_ns = time_ns()

            # Go to next mode (IDLE_STATE)
            if not FLAG_STAY_IN_FIRST_MODE and time_ns() - mode_duration_last_time_ns > ROBOT_FOLLOWS_DURATION_MS*1_000_000:
                robot_follows_state_init_done = False
                game_mode = GameMode.IDLE_STATE

                mode_duration_last_time_ns = time_ns()

        elif game_mode == GameMode.TEST_CMD:
            input1 = input()
            type = input1[0]
            if type == 'p':
                x, y, z = input1[1:].split(',')
                if robot.moveBaseToXYZ((float(x), float(y), float(z))) != 0:
                    print("Error sending message")
            elif type == 'c':
                z = input1[1:]
                if robot.moveBaseToXYZ((0, 0, float(z))) != 0:
                    print("Error sending message")
            elif type == 'f':
                x, y = input1[1:].split(',')
                if robot.moveAllAxesTo(float(x), float(y), robot.operational_space.z_axis_max) != 0:
                    print("Error sending message")
            elif type == 'a':
                a, b, c = input1[1:].split(',')
                if robot.moveAllAxesTo(float(a), float(b), float(c)) != 0:
                    print("Error sending message")
            elif type == 'z':
                a = input1[1:]
                if robot.moveAllAxesTo(float(a), float(a), float(a)) != 0:
                    print("Error sending message")

        updateScreen()

    GPIO.cleanup()
    pygame.quit()
