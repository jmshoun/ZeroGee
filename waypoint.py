import math

import pygame
from pygame.math import Vector2

import gfx
import config

settings = config.DisplaySettings()


class Gate(object):
    STATUS_LAST = 0
    STATUS_NEXT = 1
    STATUS_OTHER = 2

    MINIMUM_DISTANCE_FROM_CENTER = 10

    def __init__(self, position, angular_position, status=STATUS_OTHER, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = Vector2(position)
        self.angular_position = angular_position
        self.status = status
        self.last_side = 0

    @classmethod
    def from_dict(cls, dict_):
        return cls(dict_["position"], dict_["angle"])

    def update(self, ship_position):
        ship_position_rotated = ship_position.rotate(self.angular_position)
        gate_position_rotated = self.position.rotate(self.angular_position)
        current_side = ship_position_rotated.x - gate_position_rotated.x
        distance_from_center = abs(ship_position_rotated.y - gate_position_rotated.y)
        switched_sides = (current_side * self.last_side) < 0
        status_updated = (self.status == self.STATUS_NEXT
                          and distance_from_center < self.MINIMUM_DISTANCE_FROM_CENTER
                          and switched_sides)
        self.last_side = current_side
        return status_updated


class GateSprite(Gate, gfx.LevelSprite):
    def __init__(self, panel, *args, **kwargs):
        super().__init__(panel=panel, *args, **kwargs)
        self.images = [self._load_image('gate-last'), self._load_image('gate-next'),
                       self._load_image('gate-other')]
        self.rect = self.images[0].get_rect()

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, position=dict_["position"], angular_position=dict_["angle"])

    def _load_image(self, image_name):
        image = pygame.image.load('images/' + image_name + '.png')
        image.convert()
        rotated_image = pygame.transform.rotozoom(image, self.angular_position - 90,
                                                  settings.scale_factor)
        return rotated_image

    @property
    def image(self):
        return self.images[self.status]


class Proxy(object):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    DEFAULT_ACTIVATION_RADIUS = 7

    def __init__(self, position, status=STATUS_INACTIVE, activation_radius=None, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.position = Vector2(position)
        self.status = status
        self.activation_radius = activation_radius or self.DEFAULT_ACTIVATION_RADIUS

    @classmethod
    def from_dict(cls, dict_):
        return cls(dict_["position"], dict_.get("activation_radius"))

    def update(self, ship_position):
        if self.status == self.STATUS_ACTIVE:
            return False
        distance = (self.position - ship_position).length()
        status_updated = distance < self.activation_radius
        if status_updated:
            self.status = self.STATUS_ACTIVE
        return status_updated


class ProxySprite(Proxy, gfx.LevelSprite):
    def __init__(self, panel, *args, **kwargs):
        super().__init__(panel=panel, *args, **kwargs)
        self.images = [self._load_image('proxy-inactive'), self._load_image('proxy-active')]
        self.rect = self.images[0].get_rect()

    def _load_image(self, image_name):
        image = pygame.image.load('images/' + image_name + '.png')
        image.convert()
        scale = (settings.scale_factor * 0.5
                 * self.activation_radius / self.DEFAULT_ACTIVATION_RADIUS)
        image = pygame.transform.rotozoom(image, 0, scale)
        return image

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, position=dict_["position"],
                   activation_radius=dict_.get("activation_radius"))


class Splits(object):
    def __init__(self, num_waypoints, split_times=None, final_time=math.nan, status="Incomplete"):
        self.current_waypoint = 0
        self.split_times = split_times if split_times else [math.nan] * num_waypoints
        self.final_time = final_time
        self.status = status

    @classmethod
    def from_dict(cls, dict_):
        return cls(len(dict_["split_times"]), dict_["split_times"], dict_["final_time"],
                   dict_["status"])

    def update(self, current_time, waypoints_complete):
        while self.current_waypoint < waypoints_complete:
            self.split_times[self.current_waypoint] = current_time
            self.current_waypoint += 1

    def set_final_time(self, final_time):
        self.final_time = final_time
        self.status = "Finished"

    def as_dict(self):
        return {"split_times": self.split_times,
                "final_time": self.final_time,
                "status": self.status}
