#!/usr/bin/env python3

import pygame
from pygame.locals import *

import ScaleConversion as SC
from InputDevice import Touchfoil, Mouse, IInputDevice
from OutputDevice import DeltaRobot, OperationalSpace


BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)


# Screen setup
DISPLAY_WIDTH: int = 1440
DISPLAY_HEIGHT: int = 900

def updateScreen() -> None:
    """Update position text and dot according to current input device position
    """
    screen.fill(GRAY)
    position_img = font.render(position_text, True, RED)
    position_rect = position_img.get_rect()
    position_rect.topleft = (20, 40)
    screen.blit(position_img, position_rect)
    pygame.draw.circle(screen, BLACK, (input_device.x, input_device.y), 3)
    pygame.display.update()

pygame.init()
# If set_mode is raising "pygame.error: Unable to open a console terminal",
# and the python file is launched through ssh, the reason is there is no DISPLAY set.
# Run "export DISPLAY=:0" through ssh and try again.
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.toggle_fullscreen()
font = pygame.font.SysFont(None, 24)
position_text = 'Position here'


# Input device
def updateCallback(device: IInputDevice) -> None:
    """Function called when the input device fires a event indicating a new position

    Args:
        device (IInputDevice): the device itself (should not usually be set)
    """
    print("updateCallback(device) called")
    global position_text
    position_text = f'Position: {device.x}, {device.y}'

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

robot = DeltaRobot(A_axis_id=0xC0FFEE, B_axis_id=0xCACA0, C_axis_id=0xC0CA,
                   A_encoder_id=0x1, B_encoder_id=0x2, C_encoder_id=0x3,
                   sniff_traffic=False)
robot.callbackUpdate = onRobotPositionChanged

def screenToRobot(input_device: IInputDevice, robot: DeltaRobot) -> tuple[float, float]:
    x = SC.remap(0, input_device.screen_width, robot.operational_space.x_axis_min, robot.operational_space.x_axis_max, input_device.x)
    y = SC.remap(0, input_device.screen_height, robot.operational_space.y_axis_min, robot.operational_space.y_axis_max, input_device.y)
    
    return (x,y)

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