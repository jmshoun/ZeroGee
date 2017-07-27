#!/usr/bin/env python3

import pygame
from pygame.math import Vector2

import config

settings = config.DisplaySettings()
BOX_TIMER = 5
BOX_SIZE = 12
START_COLOR = 50
FINISH_COLOR = 255


class FinishBox(object):
    def __init__(self, panel, position):
        self.panel = panel

        self.position = Vector2(position) / settings.meters_per_pixel
        self.image_rect = pygame.Rect(0, 0, BOX_SIZE / settings.meters_per_pixel,
                                      BOX_SIZE / settings.meters_per_pixel)
        self.location_rect = self.image_rect.copy()
        self.location_rect.center = self.position
        self.rect = self.image_rect.copy()
        self.image = pygame.Surface((self.image_rect.width, self.image_rect.height))
        
        self.color = START_COLOR
        pygame.draw.rect(self.image, (self.color, self.color, self.color), self.image_rect)
        self.timer = 0
        self.locked = True
        self.finished = False
    
    def update(self, ship_position):
        if self.locked:
            return
        needs_drawing = False
        
        if self.location_rect.collidepoint(ship_position):
            self.timer = min(self.timer + settings.tick_size, BOX_TIMER)
            if self.timer == BOX_TIMER:
                self.finished = True
            needs_drawing = True
        elif self.timer > 0:
            self.timer = 0
            needs_drawing = True
        
        if needs_drawing:
            self.color = START_COLOR + (self.timer / BOX_TIMER) * (FINISH_COLOR - START_COLOR)
            pygame.draw.rect(self.image, (self.color, self.color, self.color), self.image_rect)
    
    def draw(self, camera_position):
        self.rect.center = self.position - camera_position
        self.panel.blit(self.image, self.rect)
