#!/usr/bin/env python3

import pygame
from pygame.locals import *

import Level

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1360, 768), pygame.FULLSCREEN)
pygame.display.set_caption('ZeroGee')

clock = pygame.time.Clock()
level = Level.Level(screen)

while not level.ship.finished:
    pygame.event.get()
    
    level.update()
    level.draw()
    
    pygame.display.flip()
    clock.tick(50)