#!/usr/bin/env python3

from screen_convertions import *
import pygame
from pygame.locals import *
from collections import namedtuple


Point = namedtuple("Point", "x y")

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

DISPLAY_WIDTH = 1440
DISPLAY_HEIGHT = 900

pygame.init()
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.toggle_fullscreen()
font = pygame.font.SysFont(None, 24)


cursor_position = Point(0, 0)
cursor_text = 'cursor'
img_cursor = font.render(cursor_text, True, BLACK)
rect_cursor = img_cursor.get_rect()
rect_cursor.topleft = (20, 20)

touch_position = Point(0, 0)
touch_text = 'touch'
img_touch = font.render(touch_text, True, RED)
rect_touch = img_touch.get_rect()
rect_touch.topleft = (20, 40)


running = True
background = GRAY


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        elif event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            cursor_position = Point(x, y)

            touch_x = int(remap(DISPLAY_HEIGHT, 0, 0, DISPLAY_WIDTH, y))
            touch_y = int(remap(0, DISPLAY_WIDTH, 0, DISPLAY_HEIGHT, x))

            touch_position = Point(touch_x, touch_y)

        # elif event.type == pygame.FINGERDOWN:
        #     finger_x, finger_y = event.pos
        #     mousePosition = Point(1440-finger_y, finger_x)
        #     print('fingerdown :' + mousePosition)

        # elif event.type == pygame.FINGERMOTION:
        #     finger_x, finger_y = event.pos
        #     mousePosition = Point(1440-finger_y, finger_x)
        #     print('fingermotion :' + mousePosition)

        # elif event.type == pygame.FINGERUP:
        #     pass

    screen.fill(background)

    cursor_text = f'Cursor: {cursor_position.x}, {cursor_position.y}'
    img_cursor = font.render(cursor_text, True, BLACK)
    screen.blit(img_cursor, rect_cursor)
    pygame.draw.circle(screen, BLACK, (cursor_position.x, cursor_position.y), 3)
    
    touch_text = f'touch: {touch_position.x}, {touch_position.y}'
    img_touch = font.render(touch_text, True, RED)
    screen.blit(img_touch, rect_touch)
    pygame.draw.circle(screen, RED, (touch_position.x, touch_position.y), 3)

    pygame.display.update()


pygame.quit()