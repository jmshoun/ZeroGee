#!/usr/bin/env python3

import pygame
from pygame.locals import *

import Level
import config

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1360, 768), pygame.FULLSCREEN)
pygame.display.set_caption('ZeroGee')

clock = pygame.time.Clock()
level = Level.Level(screen, "levels/circle.yaml")


def check_for_termination():
    pressed_keys = pygame.key.get_pressed()
    return pressed_keys[pygame.K_ESCAPE]

while not check_for_termination():
    pygame.event.get()
    
    level.update()
    level.draw()
    
    pygame.display.flip()
    clock.tick(1 / config.TICK_SIZE)
