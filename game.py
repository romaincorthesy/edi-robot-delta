#!/usr/bin/env python3

import pygame
from pygame.locals import *
from collections import namedtuple
from pprint import pprint

Point = namedtuple("Point", "x y")

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

mousePosition = Point(0, 0)

pygame.init()
screen = pygame.display.set_mode((640, 240))
font = pygame.font.SysFont(None, 24)

mousePositionText = 'position'
img = font.render(mousePositionText, True, RED)

rect = img.get_rect()
rect.topleft = (20, 20)

running = True
background = GRAY

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

        if event.type == MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            mousePosition = Point(x, y)

    screen.fill(background)

    mousePositionText = f'Pos: {mousePosition.x}, {mousePosition.y}'
    img = font.render(mousePositionText, True, RED)
    screen.blit(img, rect)

    pygame.display.update()

    print(mousePositionText)

pygame.quit()
