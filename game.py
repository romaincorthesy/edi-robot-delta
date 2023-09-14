#!/usr/bin/env python3

from ScreenConversion import *
import pygame
from pygame.locals import *

from InputDevice import Touchfoil, Mouse


BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Screen setup
DISPLAY_WIDTH = 1440
DISPLAY_HEIGHT = 900

def updateScreen():
    screen.fill(GRAY)
    position_img = font.render(position_text, True, RED)
    position_rect = position_img.get_rect()
    position_rect.topleft = (20, 40)
    screen.blit(position_img, position_rect)
    pygame.draw.circle(screen, BLACK, (input_device.x, input_device.y), 3)
    pygame.display.update()

pygame.init()
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.toggle_fullscreen()
font = pygame.font.SysFont(None, 24)
position_text = 'Position here'

# Input device
def updateCallback(device):
    print("updateCallback(device) called")
    global position_text
    position_text = f'Position: {device.x}, {device.y}'

input_device = Touchfoil(screen_height=DISPLAY_HEIGHT, screen_width=DISPLAY_WIDTH)
# input_device = Mouse(screen_height=DISPLAY_HEIGHT, screen_width=DISPLAY_WIDTH)
input_device.callbackUpdate = updateCallback

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