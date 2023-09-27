#!/usr/bin/env python3

import pygame
from pygame.locals import *
from time import time_ns
from math import sqrt
from enum import Enum
import json

import ScaleConversion as SC
from InputDevice import Touchfoil, Mouse, IInputDevice
from OutputDevice import DeltaRobot

# Color constants
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Screen setup
DISPLAY_WIDTH: int = 1440
DISPLAY_HEIGHT: int = 900

# User screen position setup
USER_DIFF_THRESHOLD: int = 5
user_x: int = 0
user_y: int = 0

# Robot screen position setup
robot_x: int = 0
robot_y: int = 0
FAKE_ROBOT_DELAY_MS: int = 100
last_time_ns: int = time_ns()


class GameMode(Enum):
    STD_EXPO_MODE = 0
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

    drawText(f'Robot: {robot_x}, {robot_y}', (20, 50), RED)
    pygame.draw.circle(screen, RED, (robot_x, robot_y), 6)

    drawText(f'User: {user_x}, {user_y}', (20, 20), BLACK)
    pygame.draw.circle(screen, BLACK, (user_x, user_y), 3)

    if winner == "user":
        userWon()
    elif winner == "robot":
        robotWon()

    pygame.display.update()


# Input device
def updateCallback(device: IInputDevice) -> None:
    """Function called when the input device fires a event indicating a new position

    Args:
        device (IInputDevice): the device itself (should not usually be set)
    """
    # print("callback input")

    global user_x, user_y, robot_x, robot_y, winner, last_time_ns, dxy

    if game_mode == GameMode.ROBOT_FOLLOWS:
        if dxy > DELTA_POSITION_THRESHOLD:
            # User wins against robot
            winner = "user"

        # Fake robot movement with delay
        if time_ns() - last_time_ns > FAKE_ROBOT_DELAY_MS*1_000_000:
            robot_x = device.x
            robot_y = device.y
            last_time_ns = time_ns()

        # Only send a new position message through CAN if the input position has moved enough
        if abs(device.x - user_x) > USER_DIFF_THRESHOLD or abs(device.y - user_y) > USER_DIFF_THRESHOLD:
            # print(f"x: {device.x} - {user_x} = {device.x - user_x}  y: {device.y} - {user_y} = {device.y - user_y}")
            user_x = device.x
            user_y = device.y

            x, y = screenToRobot(input_device, robot)
            if robot.moveBaseToXYZ((x, y, robot.operational_space.z_axis_max)) != 0:
                print("Error sending message")


# input_device = Touchfoil(screen_height=DISPLAY_HEIGHT, screen_width=DISPLAY_WIDTH)
input_device = Mouse(screen_height=DISPLAY_HEIGHT, screen_width=DISPLAY_WIDTH)
input_device.callbackUpdate = updateCallback


# Output device
def onRobotPositionChanged(pos: tuple[float, float, float]) -> None:
    """Function called when the robot's encoder position has changed

    Args:
        pos (tuple[float, float, float]): the new x,y,z position in the robot operational space
    """
    x, y, z = pos
    print(f"New position: {x}, {y}, {z}")

    global robot_x, robot_y
    robot_x, robot_y = robotToScreen(robot, input_device)


robot = DeltaRobot(A_motor_id=0x11, B_motor_id=0x12, C_motor_id=0x13,
                   A_encoder_id=0x11, B_encoder_id=0x12, C_encoder_id=0x13,
                   sniff_traffic=False)
# robot.callbackUpdate = onRobotPositionChanged


def screenToRobot(input_device: IInputDevice, robot: DeltaRobot, force_value: tuple[int, int] = None) -> tuple[float, float]:
    """Convert from screen to robot coordinate system. 

    Args:
        input_device (IInputDevice): an input device from which to convert the x and y properties
        robot (DeltaRobot): a robot with an operational space to convert to

    Returns:
        tuple[float, float]: a pair x,y in the robot's coordinate system
    """
    if force_value != None:
        x_in = force_value[0]
        y_in = force_value[1]
    else:
        x_in = input_device.x
        y_in = input_device.y
    x = SC.remap(0, input_device.screen_width, robot.operational_space.x_axis_min,
                 robot.operational_space.x_axis_max, x_in)
    y = SC.remap(0, input_device.screen_height, robot.operational_space.y_axis_min,
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


def userWon() -> None:
    """Called when the user has outsped the robot"""
    drawText('Vous avez gagné !', (700, 450), BLACK)


def robotWon() -> None:
    """Called when the robot has outsped the user"""
    drawText('Vous avez perdu ! Vous êtes trop lent', (700, 450), BLACK)


# Load robot movement path
path = []
with open("./path.json") as f:
    path = json.load(f)


def getPathPoint(path, i):
    return (path[i][0] + DISPLAY_WIDTH // 2, path[i][1] + DISPLAY_HEIGHT // 2)


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
    elif arg == "-r" or arg == "--robot-follows":
        print("Running in robot-follows: try to outspeed the robot")
        game_mode: GameMode = GameMode.ROBOT_FOLLOWS
    elif arg == "-t" or arg == "--test-cmd":
        print("Running in test mode\n--------------------\nAvailable commands:\n\
    p - Position:   p0,0,0.200   = moveBaseToXYZ(0, 0, 0.200) [m]\n\
    f - Flat plane: f0.010,0.020 = moveBaseToXYZ(0.010, 0.020, z_max) [m]\n\
    a - Angles:     a0,0,30      = moveAllAxesTo(0, 0, 30) [°]\n\
    z - Z axis:     z20          = moveAllAxesTo(20, 20, 20) [°]\n")
        game_mode: GameMode = GameMode.TEST_CMD
    else:
        print("Running without known args, standard use (expo)\n")
        game_mode: GameMode = GameMode.STD_EXPO_MODE
        raise NotImplementedError(
            "GameMode.STD_EXPO_MODE not yet implemented, run with -u, -r or -t")

    pygame.init()
    # If set_mode is raising "pygame.error: Unable to open a console terminal",
    # and the python file is launched through ssh, the reason is there is no DISPLAY set.
    # Run "export DISPLAY=:0" through ssh and try again.
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.toggle_fullscreen()
    font = pygame.font.SysFont(None, 24)

    DELTA_POSITION_THRESHOLD: int = 150
    winner = ""
    current_speed: float = 1.0
    dxy = 0.0
    i = 0

    # Main loop
    running = True
    while running:
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

        if game_mode == GameMode.USER_FOLLOWS:
            if dxy > DELTA_POSITION_THRESHOLD:
                # Robot wins against user
                winner = "robot"

            if time_ns() - last_time_ns > 1_000_000_000*current_speed:
                robot_x, robot_y = getPathPoint(path, i)
                print(f"New point: {robot_x}, {robot_y}")
                x, y = screenToRobot(input_device, robot, (robot_x, robot_y))

                if robot.moveBaseToXYZ((x, y, robot.operational_space.z_axis_max)) != 0:
                    print("Error sending message")

                i += 1
                i %= len(path)
                if current_speed > 0.02:
                    current_speed -= 0.02
                last_time_ns = time_ns()
        elif game_mode == GameMode.TEST_CMD:
            input1 = input()
            type = input1[0]
            if type == 'p':
                x, y, z = input1[1:].split(',')
                if robot.moveBaseToXYZ((float(x), float(y), float(z))) != 0:
                    print("Error sending message")
            elif type == 'f':
                a = input1[1:]
                if robot.moveAllAxesTo(float(a), float(a), float(a)) != 0:
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

    pygame.quit()
