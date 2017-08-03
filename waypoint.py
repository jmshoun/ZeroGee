import pygame
from pygame.math import Vector2

import config

settings = config.DisplaySettings()


class Gate(object):
    STATUS_LAST = 0
    STATUS_NEXT = 1
    STATUS_OTHER = 2

    def __init__(self, panel, position, angular_position, status=STATUS_OTHER):
        self.panel = panel

        self.position = Vector2(position)
        self.angular_position = angular_position

        self.images = [self._init_image('gate-last'), self._init_image('gate-next'),
                       self._init_image('gate-other')]
        self.rect = self.images[0].get_rect()

        self.status = status
        self.last_side = 0

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["position"], dict_["angle"])

    def _init_image(self, image_name):
        image = pygame.image.load('images/' + image_name + '.png')
        image.convert()
        image = pygame.transform.rotozoom(image, self.angular_position, settings.scale_factor)
        return image

    def update(self, ship_position):
        status_updated = False
        ship_position_rotated = ship_position.rotate(self.angular_position)
        gate_position_rotated = self.position.rotate(self.angular_position)
        side = ship_position_rotated.y - gate_position_rotated.y
        distance_from_center = abs(ship_position_rotated.x - gate_position_rotated.x)
        if (side * self.last_side < 0 and distance_from_center < 10
                and self.status == self.STATUS_NEXT):
            status_updated = True
        self.last_side = side

        return status_updated

    def draw(self, camera_position):
        self.rect.center = (self.position - camera_position) / settings.meters_per_pixel
        self.panel.blit(self.images[self.status], self.rect)


class Proxy(object):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1

    def __init__(self, panel, position, status=STATUS_INACTIVE, activation_radius=7):
        self.panel = panel
        self.position = Vector2(position)
        self.status = status
        self.activation_radius = activation_radius
        self.images = [self._init_image('proxy-inactive'), self._init_image('proxy-active')]
        self.rect = self.images[0].get_rect()

    def _init_image(self, image_name):
        image = pygame.image.load('images/' + image_name + '.png')
        image.convert()
        image = pygame.transform.rotozoom(image, 0, settings.scale_factor * 0.5)
        return image

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["position"])

    def update(self, ship_position):
        if self.status == self.STATUS_ACTIVE:
            return False
        distance = (self.position - ship_position).length()
        status_updated = distance < self.activation_radius
        if status_updated:
            self.status = self.STATUS_ACTIVE
        return status_updated

    def draw(self, camera_position):
        self.rect.center = (self.position - camera_position) / settings.meters_per_pixel
        self.panel.blit(self.images[self.status], self.rect)
