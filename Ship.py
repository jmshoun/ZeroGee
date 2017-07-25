#!/usr/bin/env python3

import math

import pygame

import config

settings = config.DisplaySettings()
RADIANS_TO_DEGREES = 180 / math.pi


class Ship(object):
    SCALE_FACTOR = 0.6
    DRY_MASS = 1000.0                   # kg
    STARTING_FUEL_MASS = 200.0          # kg
    LENGTH = 2.5                        # m
    ROTATE_THRUSTER_POSITION = 2.0      # m outboard from center of mass
    ROTATE_INERTIA_FACTOR = LENGTH ** 2 / (ROTATE_THRUSTER_POSITION * 12)

    EXHAUST_VELOCITY = 1040.0           # m/sec
    THRUST_FUEL_RATE = 4.0              # kg/sec
    ROTATE_FUEL_RATE = 0.8              # kg/sec
    
    FORCE = EXHAUST_VELOCITY * THRUST_FUEL_RATE
    TORQUE = EXHAUST_VELOCITY * ROTATE_FUEL_RATE * ROTATE_THRUSTER_POSITION
    
    def __init__(self, panel, position, position_angular):
        self.panel = panel
        self.center_x = panel.get_rect().width / 2
        self.center_y = panel.get_rect().height / 2
        self.image = pygame.image.load('images/A5.png').convert()
        self.image = pygame.transform.rotozoom(self.image, 0, self.SCALE_FACTOR)
        self.rect = self.image.get_rect()
        
        self.fuel_mass = self.STARTING_FUEL_MASS
        self.engine_on = False
        self.left_thruster_on = False
        self.right_thruster_on = False
        self.main_flame = Flame(self.panel, 0, 35)
        self.left_rear_flame = Flame(self.panel, -35, 15, math.pi / 2, 0.18)
        self.right_rear_flame = Flame(self.panel, 35, 15, -math.pi / 2, 0.18)
        self.left_front_flame = Flame(self.panel, -10, -15, math.pi / 2, 0.12)
        self.right_front_flame = Flame(self.panel, 10, -15, -math.pi / 2, 0.12)

        self.velocity_x, self.velocity_y = 0, 0
        self.position_x, self.position_y = position
        self.velocity_angular = 0
        self.position_angular = position_angular / RADIANS_TO_DEGREES
    
    def status(self):
        speed = math.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2) * settings.meters_per_pixel
        return speed, self.fuel_mass
    
    def camera_position(self):
        absolute_offset_x = abs(self.velocity_x) ** .6 * .5
        offset_x = math.copysign(absolute_offset_x, self.velocity_x)
        
        absolute_offset_y = abs(self.velocity_y) ** .6 * .5
        offset_y = math.copysign(absolute_offset_y, self.velocity_y)
        
        return [offset_x - self.center_x + self.position_x,
                offset_y - self.center_y + self.position_y]
    
    def position(self):
        return self.position_x, self.position_y
    
    def update(self):
        if self.fuel_mass > 0:
            self._handle_keyboard_input()

        self.position_angular += self.velocity_angular * settings.tick_size
        self.position_x += self.velocity_x * settings.tick_size
        self.position_y += self.velocity_y * settings.tick_size

        self.main_flame.update(self.engine_on)
        self.left_rear_flame.update(self.left_thruster_on)
        self.right_front_flame.update(self.left_thruster_on)
        self.right_rear_flame.update(self.right_thruster_on)
        self.left_front_flame.update(self.right_thruster_on)
    
    def _handle_keyboard_input(self):
        pressed_keys = pygame.key.get_pressed()
        mass = self.DRY_MASS + self.fuel_mass
        acceleration = self.FORCE / mass / settings.meters_per_pixel * settings.tick_size
        acceleration_angular = (self.TORQUE / (mass * self.ROTATE_INERTIA_FACTOR)
                                * settings.tick_size)
        
        if pressed_keys[pygame.K_LEFT]:
            self.velocity_angular += acceleration_angular
            self.fuel_mass -= self.ROTATE_FUEL_RATE * settings.tick_size
        if pressed_keys[pygame.K_RIGHT]:
            self.velocity_angular -= acceleration_angular
            self.fuel_mass -= self.ROTATE_FUEL_RATE * settings.tick_size
        if pressed_keys[pygame.K_UP]:
            self.velocity_y -= acceleration * math.cos(self.position_angular)
            self.velocity_x -= acceleration * math.sin(self.position_angular)
            self.fuel_mass -= self.THRUST_FUEL_RATE * settings.tick_size
        self.engine_on = pressed_keys[pygame.K_UP] and self.fuel_mass > 0
        self.left_thruster_on = pressed_keys[pygame.K_LEFT] and self.fuel_mass > 0
        self.right_thruster_on = pressed_keys[pygame.K_RIGHT] and self.fuel_mass > 0
    
    def draw(self, camera_position):
        camera_x, camera_y = camera_position
        
        rotated_image = pygame.transform.rotozoom(self.image,
                                                  self.position_angular * RADIANS_TO_DEGREES,
                                                  settings.scale_factor)
        rotated_image.set_colorkey((0, 0, 0))
        tmp_rect = rotated_image.get_rect()
        rotated_rect = self.rect.inflate(tmp_rect.width - self.rect.width,
                                         tmp_rect.height - self.rect.height)
        
        rotated_rect.center = (self.position_x - camera_x, self.position_y - camera_y)
        
        self.panel.blit(rotated_image, rotated_rect)
        self.main_flame.draw(rotated_rect.center, self.position_angular)
        self.left_rear_flame.draw(rotated_rect.center, self.position_angular)
        self.right_rear_flame.draw(rotated_rect.center, self.position_angular)
        self.left_front_flame.draw(rotated_rect.center, self.position_angular)
        self.right_front_flame.draw(rotated_rect.center, self.position_angular)


class Flame(object):
    def __init__(self, panel, offset_x, offset_y, offset_angle=math.pi, scale_factor=0.4):
        self.panel = panel
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_angle = offset_angle
        self.scale_factor = scale_factor
        self.images = [self._load_image(i) for i in range(1, 31)]
        self.current_index = None

    def update(self, engine_on):
        if self.current_index is None:
            self.current_index = 1 if engine_on else None
        elif self.current_index < 10:
            self.current_index = self.current_index + 1 if engine_on else 29 - self.current_index
        elif self.current_index < 20:
            self.current_index = self.current_index + 1 if engine_on else 21
        elif self.current_index == 20:
            self.current_index = 10 if engine_on else 21
        elif self.current_index < 30:
            self.current_index = 31 - self.current_index if engine_on else self.current_index + 1
        if self.current_index == 30:
            self.current_index = None

    def _load_image(self, ndx):
        filename = 'images/blue_flame/{0:04}.png'.format(ndx)
        image = pygame.image.load(filename).convert()
        return pygame.transform.rotozoom(image, 0, self.scale_factor)

    def draw(self, center, angular_position):
        if not self.current_index:
            return

        center_x, center_y = center
        pos_x, pos_y = (center_x + self.offset_x * math.cos(angular_position)
                        + self.offset_y * math.sin(angular_position),
                        center_y + self.offset_y * math.cos(angular_position)
                        - self.offset_x * math.sin(angular_position))
        angle = angular_position + self.offset_angle
        rotated_image = pygame.transform.rotozoom(self.images[self.current_index],
                                                  angle * RADIANS_TO_DEGREES,
                                                  settings.scale_factor)
        rotated_image.set_colorkey((0, 0, 0))
        rotated_rect = rotated_image.get_rect()
        rotated_rect.center = pos_x, pos_y
        self.panel.blit(rotated_image, rotated_rect)
