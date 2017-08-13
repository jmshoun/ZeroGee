#!/usr/bin/env python3

import sys

import yaml
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

with open(sys.argv[1]) as course_file:
    course_dict = yaml.load(course_file.read())
with open(sys.argv[2]) as ship_file:
    ship_dict = yaml.load(ship_file.read())
level = level.Level(screen, course_dict, ship_dict)


def check_for_termination():
    pressed_keys = pygame.key.get_pressed()
    return pressed_keys[pygame.K_ESCAPE]

while not check_for_termination():
    pygame.event.get()
    
    level.update()
    level.draw()
    
    pygame.display.flip()
    clock.tick(1 / settings.tick_size)
