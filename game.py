#!/usr/bin/env python3

import pygame
from pygame.locals import *
from time import time_ns
from math import sqrt

import ScaleConversion as SC
from InputDevice import Touchfoil, Mouse, IInputDevice
from OutputDevice import DeltaRobot, OperationalSpace


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


def drawText(text: str, topleft: tuple[int, int], color: tuple[int, int, int]):
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

    pygame.display.update()


pygame.init()
# If set_mode is raising "pygame.error: Unable to open a console terminal",
# and the python file is launched through ssh, the reason is there is no DISPLAY set.
# Run "export DISPLAY=:0" through ssh and try again.
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.toggle_fullscreen()
font = pygame.font.SysFont(None, 24)

user_robot_d_pos: float = 0
DELTA_POSITION_THRESHOLD: int = 150
winner = ""


# Input device
def updateCallback(device: IInputDevice) -> None:
    """Function called when the input device fires a event indicating a new position

    Args:
        device (IInputDevice): the device itself (should not usually be set)
    """
    global user_x, user_y, robot_x, robot_y, user_robot_d_pos, winner, last_time_ns

    # Update user-robot position error
    dx = user_x - robot_x
    dy = user_y - robot_y
    dxy = sqrt(dx*dx + dy*dy)
    if dxy > DELTA_POSITION_THRESHOLD:
        # User wins against robot
        winner = "user"

    # Fake robot movement
    if time_ns()-last_time_ns > FAKE_ROBOT_DELAY_MS*1_000_000:
        robot_x = device.x
        robot_y = device.y
        last_time_ns = time_ns()

    if abs(device.x - user_x) > USER_DIFF_THRESHOLD or abs(device.y - user_y) > USER_DIFF_THRESHOLD:
        # print(f"x: {device.x} - {user_x} = {device.x - user_x}  y: {device.y} - {user_y} = {device.y - user_y}")
        user_x = device.x
        user_y = device.y

        # print("updateCallback(device) called")
        x, y = screenToRobot(input_device, robot)
        if robot.moveBaseToXYZ((x, y, robot.operational_space.z_axis_max)) != 0:
            print("Error sending message")


# input_device = Touchfoil(screen_height=DISPLAY_HEIGHT, screen_width=DISPLAY_WIDTH)
input_device = Mouse(screen_height=DISPLAY_HEIGHT, screen_width=DISPLAY_WIDTH)
input_device.callbackUpdate = updateCallback


# Output device
def onRobotPositionChanged(pos: tuple[float, float, float]) -> None:
    x, y, z = pos
    print(f"New position: {x}, {y}, {z}")

    global robot_x, robot_y
    robot_x, robot_y = robotToScreen(robot, input_device)


robot = DeltaRobot(A_axis_id=0x1, B_axis_id=0x2, C_axis_id=0x3,
                   A_encoder_id=0x1, B_encoder_id=0x2, C_encoder_id=0x3,
                   sniff_traffic=False)
# robot.callbackUpdate = onRobotPositionChanged


def screenToRobot(input_device: IInputDevice, robot: DeltaRobot) -> tuple[float, float]:
    x = SC.remap(0, input_device.screen_width, robot.operational_space.x_axis_min,
                 robot.operational_space.x_axis_max, input_device.x)
    y = SC.remap(0, input_device.screen_height, robot.operational_space.y_axis_min,
                 robot.operational_space.y_axis_max, input_device.y)

    return (x, y)


def robotToScreen(robot: DeltaRobot, input_device: IInputDevice) -> tuple[float, float]:
    x = SC.remap(robot.operational_space.x_axis_min,
                 robot.operational_space.x_axis_max, 0, input_device.screen_width, robot.x)
    y = SC.remap(robot.operational_space.y_axis_min,
                 robot.operational_space.y_axis_max, 0, input_device.screen_height, robot.y)

    return (x, y)


def userWon() -> None:
    drawText('Vous avez gagné !', (700, 450), BLACK)


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

    updateScreen()

pygame.quit()
