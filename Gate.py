#!/usr/bin/env python3

import math

import pygame

import config

RADIANS_TO_DEGREES = 180 / math.pi

STATUS_LAST = 0
STATUS_NEXT = 1
STATUS_OTHER = 2

class Gate:
    
    def __init__(self, screen, position, angular_position, status):
        self.screen = screen
        
        self.position_x, self.position_y = position
        self.position_x = self.position_x / config.METERS_PER_PIXEL
        self.position_y = self.position_y / config.METERS_PER_PIXEL
        self.angular_position = angular_position / RADIANS_TO_DEGREES
        
        self.images = [self._init_image('gate-last'), self._init_image('gate-next'),
                       self._init_image('gate-other')]
        self.rect = self.images[0].get_rect()
        
        self.status = status
        self.last_side = 0
        
    def _init_image(self, image_name):
        image = pygame.image.load('images/' + image_name + '.png')
        image.convert()
        image = pygame.transform.rotozoom(image, self.angular_position * RADIANS_TO_DEGREES,
                                          config.SCALE_FACTOR)
        
        return image
    
    def update(self, ship_position):
        status_updated = False
        ship_x, ship_y = ship_position
        
        rotated_ship_x = ship_x * math.cos(-self.angular_position) - \
                ship_y * math.sin(-self.angular_position)
        rotated_ship_y = ship_x * math.sin(-self.angular_position) + \
                ship_y * math.cos(-self.angular_position)
        gate_rotated_x = self.position_x * math.cos(-self.angular_position) - \
                self.position_y * math.sin(-self.angular_position)
        gate_rotated_y = self.position_x * math.sin(-self.angular_position) + \
                self.position_y * math.cos(-self.angular_position)
        
        side = rotated_ship_y - gate_rotated_y
        if side * self.last_side < 0 and abs(gate_rotated_x - rotated_ship_x) < 67 and \
                self.status == STATUS_NEXT:
            status_updated = True
        self.last_side = side
        
        return status_updated
    
    def draw(self, camera_position):
        camera_x, camera_y = camera_position
        self.rect.center = (self.position_x - camera_x, self.position_y - camera_y)
        self.screen.blit(self.images[self.status], self.rect)
        
        return