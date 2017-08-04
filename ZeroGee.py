#!/usr/bin/env python3

import sys

import pygame
from pygame.locals import *

import level
import config

settings = config.DisplaySettings()
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(settings.screen_resolution, pygame.FULLSCREEN)
pygame.display.set_caption('ZeroGee')

clock = pygame.time.Clock()
level = level.Level(screen, sys.argv[1])


def check_for_termination():
    pressed_keys = pygame.key.get_pressed()
    return pressed_keys[pygame.K_ESCAPE]

while not check_for_termination():
    pygame.event.get()
    
    level.update()
    level.draw()
    
    pygame.display.flip()
    clock.tick(1 / settings.tick_size)
