#!/usr/bin/env python3

import math

import pygame

RADIANS_TO_DEGREES = 180 / math.pi

class Gate:
    def __init__(self, screen, position, angular_position, status):
        self.screen = screen
        self.image_last = pygame.image.load('images/gate-last.png').convert()
        self.image_next = pygame.image.load('images/gate-next.png').convert()
        self.image_other = pygame.image.load('images/gate-other.png').convert()
        
        self.position_x, self.position_y = position
        self.angular_position = angular_position
        self.status = status
        
        if self.status == 'last':
            self.image = self.image_last
        elif self.status == 'next':
            self.image = self.image_next
        else:
            self.image = self.image_other
            
        self.image = pygame.transform.rotozoom(self.image,
                                               self.angular_position * RADIANS_TO_DEGREES, 0.5)
        self.rect = self.image.get_rect()
        self.last_side = 0
    
    def update(self, ship_position):
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
        if side * self.last_side < 0 and abs(gate_rotated_x - rotated_ship_x) < 23 and \
                self.status == 'next':
            self.status = 'last'
            self.image = self.image_last
            self.image = pygame.transform.rotozoom(self.image,
                                               self.angular_position * RADIANS_TO_DEGREES, 0.5)
        self.last_side = side
        
        return
    
    def draw(self, camera_position):
        camera_x, camera_y = camera_position
        self.rect.center = (self.position_x - camera_x, self.position_y - camera_y)
        self.screen.blit(self.image, self.rect.center)
        
        return
