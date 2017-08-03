#!/usr/bin/env python3

import math

import pygame
from pygame.math import Vector2

import config

settings = config.DisplaySettings()
RADIANS_TO_DEGREES = 180 / math.pi

LEFT = 1
RIGHT = -1


class Ship(object):
    SCALE_FACTOR = 0.6
    DRY_MASS = 1000.0                   # kg
    STARTING_FUEL_MASS = 200.0          # kg
    LENGTH = 2.5                        # m
    ROTATE_THRUSTER_POSITION = 2.0      # m outboard from center of mass
    ROTATE_INERTIA_FACTOR = LENGTH ** 2 / (ROTATE_THRUSTER_POSITION * 12)

    EXHAUST_VELOCITY = 1860.0           # m/sec
    THRUST_FUEL_RATE = 4.0              # kg/sec
    ROTATE_FUEL_RATE = 0.5              # kg/sec

    OFFSET_STRENGTH = 0.2
    
    def __init__(self, panel, position, position_angular):
        self.panel = panel
        self.center = Vector2(panel.get_rect().center) * settings.meters_per_pixel
        self.image = pygame.image.load('images/A5.png').convert()
        self.image = pygame.transform.rotozoom(self.image, -90, self.SCALE_FACTOR)
        
        self.fuel_tank = FuelTank(10, 200, fuel_mass=200)
        self.main_engine = MainEngine(self.panel, self.THRUST_FUEL_RATE,
                                      self.EXHAUST_VELOCITY, -35, 0.4)
        self.left_engine = RotationEngine(self.panel, self.ROTATE_FUEL_RATE, self.EXHAUST_VELOCITY,
                                          self.ROTATE_THRUSTER_POSITION, Vector2(15, 10),
                                          Vector2(-15, -35), 0.12, LEFT)
        self.right_engine = RotationEngine(self.panel, self.ROTATE_FUEL_RATE, self.EXHAUST_VELOCITY,
                                           self.ROTATE_THRUSTER_POSITION, Vector2(15, -10),
                                           Vector2(-15, 35), 0.12, RIGHT)

        self.velocity = Vector2(0, 0)
        self.position = Vector2(position)
        self.velocity_angular = 0
        self.position_angular = position_angular

    @property
    def rect(self):
        return self.image.get_rect()

    @property
    def status(self):
        speed = self.velocity.length()
        return speed, self.fuel_tank.fuel_mass

    @property
    def camera_position(self):
        """Camera position is the coordinate (measured in meters) of the top-left corner of the
        main panel of the display."""
        offset = Vector2(math.copysign(abs(self.velocity.x ** 0.6), self.velocity.x),
                         math.copysign(abs(self.velocity.y ** 0.6), self.velocity.y))
        return self.position - self.center + offset * self.OFFSET_STRENGTH

    @property
    def mass(self):
        return self.DRY_MASS + self.fuel_tank.mass
    
    def update(self):
        self._handle_keyboard_input()

        force = self.main_engine.force * self.fuel_tank.efficiency
        acceleration_magnitude = force / self.mass * settings.tick_size
        torque = (self.left_engine.torque - self.right_engine.torque) * self.fuel_tank.efficiency
        acceleration_angular = (torque / (self.mass * self.ROTATE_INERTIA_FACTOR)
                                * settings.tick_size * RADIANS_TO_DEGREES)

        self.velocity_angular += acceleration_angular
        self.position_angular += self.velocity_angular * settings.tick_size

        acceleration = Vector2()
        acceleration.from_polar((acceleration_magnitude, -self.position_angular))
        self.velocity += acceleration
        self.position += self.velocity * settings.tick_size
    
    def _handle_keyboard_input(self):
        burn_mass = 0
        if not self.fuel_tank.is_empty:
            pressed_keys = pygame.key.get_pressed()
            burn_mass += self.main_engine.update(pressed_keys[pygame.K_UP])
            burn_mass += self.left_engine.update(pressed_keys[pygame.K_LEFT])
            burn_mass += self.right_engine.update(pressed_keys[pygame.K_RIGHT])
        else:
            # Always update the engines so the flames will decay when fuel is exhausted.
            self.main_engine.update(False)
            self.left_engine.update(False)
            self.right_engine.update(False)
        self.fuel_tank.update(burn_mass)
    
    def draw(self, camera_position):
        rotated_image = pygame.transform.rotozoom(self.image, self.position_angular,
                                                  settings.scale_factor)
        rotated_image.set_colorkey((0, 0, 0))
        tmp_rect = rotated_image.get_rect()
        rotated_rect = self.rect.inflate(tmp_rect.width - self.rect.width,
                                         tmp_rect.height - self.rect.height)
        rotated_rect.center = (self.position - camera_position) / settings.meters_per_pixel
        
        self.panel.blit(rotated_image, rotated_rect)
        ship_center = Vector2(rotated_rect.center)
        self.main_engine.draw(ship_center, self.position_angular)
        self.left_engine.draw(ship_center, self.position_angular)
        self.right_engine.draw(ship_center, self.position_angular)


class Engine(object):
    MAX_POWER = 10
    NUM_STATES = 10

    def __init__(self, panel, fuel_rate, exhaust_velocity):
        self.panel = panel
        self.fuel_rate = fuel_rate
        self.exhaust_velocity = exhaust_velocity
        self.engine_on = False
        self.power = 0
        self.state = -1

    def update(self, key_on):
        self.engine_on = key_on
        if self.engine_on:
            if self.power < self.MAX_POWER:
                self.power += 1
            if self.power == self.MAX_POWER:
                self.state += 1
                self.state %= self.NUM_STATES
        else:
            self.state = -1
            if self.power > 0:
                self.power -= 1
        return self.power / self.MAX_POWER * self.fuel_rate * settings.tick_size

    @property
    def image_index(self):
        if self.engine_on:
            if self.power < self.MAX_POWER:
                return self.power
            else:
                return self.MAX_POWER + self.state
        elif self.power > 0:
            return 2 * self.MAX_POWER + self.NUM_STATES - self.power
        else:
            return None


class MainEngine(Engine):
    def __init__(self, panel, fuel_rate, exhaust_velocity, offset_y, scale_factor):
        super().__init__(panel, fuel_rate, exhaust_velocity)
        self.full_force = self.fuel_rate * self.exhaust_velocity
        self.flame = Flame(panel, Vector2(offset_y, 0), scale_factor=scale_factor)

    @property
    def force(self):
        return self.full_force * self.power / self.MAX_POWER

    def draw(self, center, angular_position):
        self.flame.draw(center, angular_position, self.image_index)


class RotationEngine(Engine):
    def __init__(self, panel, fuel_rate, exhaust_velocity, outboard_distance,
                 fore_offset, aft_offset, scale_factor, direction):
        super().__init__(panel, fuel_rate, exhaust_velocity)
        self.outboard_distance = outboard_distance
        self.full_torque = self.fuel_rate * self.exhaust_velocity * self.outboard_distance
        self.fore_flame = Flame(panel, fore_offset, direction * 90, scale_factor)
        self.aft_flame = Flame(panel, aft_offset, -direction * 90, scale_factor)

    @property
    def torque(self):
        return self.full_torque * self.power / self.MAX_POWER

    def draw(self, center, angular_position):
        self.fore_flame.draw(center, angular_position, self.image_index)
        self.aft_flame.draw(center, angular_position, self.image_index)


class Flame(object):
    def __init__(self, panel, offset, offset_angle=0, scale_factor=0.4):
        self.panel = panel
        self.offset = offset
        self.offset_angle = offset_angle + 90
        self.scale_factor = scale_factor
        self.images = [self._load_image(i) for i in range(1, 31)]

    def _load_image(self, ndx):
        filename = "images/blue_flame/{0:04}.png".format(ndx)
        image = pygame.image.load(filename).convert()
        return pygame.transform.rotozoom(image, 0, self.scale_factor)

    def draw(self, center, angular_position, index):
        if index is None:
            return

        offset_rotated = self.offset.rotate(-angular_position)
        position = center + offset_rotated
        angle = angular_position + self.offset_angle
        rotated_image = pygame.transform.rotozoom(self.images[index], angle,
                                                  settings.scale_factor)
        rotated_image.set_colorkey((0, 0, 0))
        rotated_rect = rotated_image.get_rect()
        rotated_rect.center = position
        self.panel.blit(rotated_image, rotated_rect)


class Fuel(object):
    def __init__(self, name, exhaust_velocity, density):
        self.name = name
        self.exhaust_velocity = exhaust_velocity
        self.density = density


FUELS = {
    "Hydrogen Peroxide": Fuel("Hydrogen Peroxide", 1860, 1.40),
    "HydroBeryllox": Fuel("HydroBeryllox", 5295, 0.24),
    "HydroFlouro": Fuel("HydroFlouro", 4697, 0.52),
    "Kerolox": Fuel("Kerolox", 3510, 1.03),
    "ChloroFlouro": Fuel("ChloroFlouro", 3356, 1.50)
}


def clamp(x, clamp_range):
    """Returns the value inside clamp_range that is closest to x."""
    clamp_min, clamp_max = clamp_range
    return clamp_min if x < clamp_min else clamp_max if x > clamp_max else x


class FuelTank(object):
    FULL_PRESSURE = 690  # KPa
    GAMMA = 1.22  # unitless

    def __init__(self, dry_mass, volume, fuel_name="Hydrogen Peroxide", fuel_mass=0):
        self.dry_mass = dry_mass
        self.volume = volume
        self.fuel = FUELS[fuel_name]
        self.fuel_mass = clamp(fuel_mass, (0, self.max_fuel_mass))
        self.max_efficiency_coefficient = self.efficiency_coefficient(self.max_fuel_mass)

    @property
    def is_empty(self):
        return self.fuel_mass <= 0

    @property
    def mass(self):
        return self.dry_mass + self.fuel_mass

    @property
    def max_fuel_mass(self):
        return self.volume * self.fuel.density

    def update(self, burn_mass):
        self.fuel_mass = max(self.fuel_mass - burn_mass, 0)

    def efficiency_coefficient(self, fuel_mass):
        if fuel_mass <= 0:
            return 0
        pressure = self.FULL_PRESSURE * fuel_mass / self.max_fuel_mass
        pressure_term = (1 / pressure) ** ((self.GAMMA - 1) / self.GAMMA)
        return math.sqrt(1 - pressure_term) if pressure_term < 1 else 0

    @property
    def efficiency(self):
        return self.efficiency_coefficient(self.fuel_mass) / self.max_efficiency_coefficient
