import math

import pygame
from pygame.math import Vector2

import config

settings = config.DisplaySettings()


def clamp(x, clamp_range):
    """Returns the value inside clamp_range that is closest to x."""
    clamp_min, clamp_max = clamp_range
    return clamp_min if x < clamp_min else clamp_max if x > clamp_max else x


class Engine(object):
    MAX_POWER = 10
    NUM_STATES = 10
    THROTTLE_STEPS = 10

    def __init__(self, panel, fuel_rate, exhaust_velocity, throttle_ratio):
        self.panel = panel
        self.fuel_rate = fuel_rate
        self.exhaust_velocity = exhaust_velocity
        self.engine_on = False
        self.power = 0
        self.state = -1

        self.throttle_ratio = throttle_ratio
        self.throttle_state = self.THROTTLE_STEPS

    def update(self, key_on, throttle_on=False):
        self._update_state(key_on)
        self._update_throttle(throttle_on)

    def _update_state(self, key_on):
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

    def _update_throttle(self, throttle_on):
        if throttle_on and self.throttle_state > 0:
            self.throttle_state -= 1
        elif not throttle_on and self.throttle_state < self.THROTTLE_STEPS:
            self.throttle_state += 1

    @property
    def throttle_factor(self):
        return (self.throttle_ratio
                + (1 - self.throttle_ratio) * (self.throttle_state / self.THROTTLE_STEPS))

    @property
    def thrust_factor(self):
        power_factor = self.power / self.MAX_POWER
        return power_factor * self.throttle_factor

    @property
    def fuel_burn(self):
        return self.thrust_factor * self.fuel_rate * settings.tick_size

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
    def __init__(self, panel, fuel_rate, exhaust_velocity, offset_y, scale_factor,
                 throttle_ratio=1.0):
        super().__init__(panel, fuel_rate, exhaust_velocity, throttle_ratio)
        self.full_force = self.fuel_rate * self.exhaust_velocity
        self.flame = Flame(panel, Vector2(offset_y, 0), scale_factor=scale_factor)

    @property
    def force(self):
        return self.full_force * self.thrust_factor

    def draw(self, center, angular_position):
        self.flame.draw(center, angular_position, self.image_index)


class RotationEngine(Engine):
    def __init__(self, panel, fuel_rate, exhaust_velocity, outboard_distance,
                 fore_offset, aft_offset, scale_factor, direction, throttle_ratio=1.0):
        super().__init__(panel, fuel_rate, exhaust_velocity, throttle_ratio)
        self.outboard_distance = outboard_distance
        self.full_torque = self.fuel_rate * self.exhaust_velocity * self.outboard_distance
        self.fore_flame = Flame(panel, fore_offset, direction * 90, scale_factor)
        self.aft_flame = Flame(panel, aft_offset, -direction * 90, scale_factor)

    @property
    def torque(self):
        return self.full_torque * self.thrust_factor

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


class FuelTank(object):
    FULL_PRESSURE = 690  # KPa
    GAMMA = 1.22         # unitless

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

    @property
    def exhaust_velocity(self):
        return self.fuel.exhaust_velocity

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
