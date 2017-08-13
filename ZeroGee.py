#!/usr/bin/env python3

import sys

import yaml
import pygame
from pygame.locals import *

import level
import profile
import config

settings = config.DisplaySettings()
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(settings.screen_resolution, pygame.FULLSCREEN)
pygame.display.set_caption('ZeroGee')

clock = pygame.time.Clock()

player_profile = profile.Profile.load("default")
course_name = sys.argv[1]
with open(course_name + ".yaml") as course_file:
    course_dict = yaml.load(course_file.read())
with open(sys.argv[2]) as ship_file:
    ship_dict = yaml.load(ship_file.read())
best_split_dict = player_profile.course_bests.get(course_name)
level = level.Level(screen, course_dict, ship_dict, best_split_dict)


def check_for_termination():
    pressed_keys = pygame.key.get_pressed()
    return pressed_keys[pygame.K_ESCAPE]

while not check_for_termination():
    pygame.event.get()
    
    level.update()
    level.draw()
    
    pygame.display.flip()
    clock.tick(1 / settings.tick_size)

last_split_dict = level.active_splits.as_dict()
if not best_split_dict or last_split_dict["final_time"] < best_split_dict["final_time"]:
    player_profile.course_bests[course_name] = last_split_dict
player_profile.save()

