#!/usr/bin/env python3

import pygame

import config

BOX_TIMER = 5
BOX_SIZE = 12
START_COLOR = 50
FINISH_COLOR = 255

class FinishBox:
    
    def __init__(self, screen, position):
        self.screen = screen
        
        self.position_x, self.position_y = position
        self.position_x = self.position_x / config.METERS_PER_PIXEL
        self.position_y = self.position_y / config.METERS_PER_PIXEL
        self.image_rect = pygame.Rect(0, 0, BOX_SIZE / config.METERS_PER_PIXEL,
                                      BOX_SIZE / config.METERS_PER_PIXEL)
        self.location_rect = self.image_rect.copy()
        self.location_rect.center = (self.position_x, self.position_y)
        self.rect = self.image_rect.copy()
        self.image = pygame.Surface((self.image_rect.width, self.image_rect.height))
        
        self.color = START_COLOR
        pygame.draw.rect(self.image, (self.color, self.color, self.color), self.image_rect)
        self.timer = 0
        self.finished = False
    
    def update(self, ship_position):
        needs_drawing = False
        
        if self.location_rect.collidepoint(ship_position):
            self.timer = min(self.timer + config.TICK_SIZE, BOX_TIMER)
            if self.timer == BOX_TIMER:
                self.finished = True
            needs_drawing = True
        elif self.timer > 0:
            self.timer = 0
            needs_drawing = True
        
        if needs_drawing:
            self.color = START_COLOR + (self.timer / BOX_TIMER) * (FINISH_COLOR - START_COLOR)
            pygame.draw.rect(self.image, (self.color, self.color, self.color), self.image_rect)
        
        return
    
    def draw(self, camera_position):
        camera_x, camera_y = camera_position
        self.rect.center = (self.position_x - camera_x, self.position_y - camera_y)
        self.screen.blit(self.image, self.rect)
        
        return