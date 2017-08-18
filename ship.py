import math

import pygame
from pygame.math import Vector2

import config
import propulsion

settings = config.DisplaySettings()
RADIANS_TO_DEGREES = 180 / math.pi

LEFT = 1
RIGHT = -1


def clamp(x, clamp_range):
    """Returns the value inside clamp_range that is closest to x."""
    clamp_min, clamp_max = clamp_range
    return clamp_min if x < clamp_min else clamp_max if x > clamp_max else x


def ship_from_dict(panel, dict_):
    ship_type = dict_["ship_class"]
    if ship_type == "Pegasus":
        return Pegasus.from_dict(panel, dict_)
    elif ship_type == "Manticore":
        return Manticore.from_dict(panel, dict_)
    else:
        raise Exception("Ship type {} does not exist.".format(ship_type))


class Ship(object):
    CAMERA_OFFSET_STRENGTH = 0.2
    # Placeholder values. All of these should be overriden, and in fact most of these values should
    # trigger runtime errors.
    SCALE_FACTOR = 0
    DRY_MASS = 0
    LENGTH = 0
    ROTATE_THRUSTER_POSITION = 0

    def __init__(self, panel, image_filename):
        # Graphical elements
        self.panel = panel
        self.panel_center = Vector2(panel.get_rect().center) * settings.meters_per_pixel
        self.image = self.load_image(image_filename)
        # Physical properties
        self.rotational_inertia_factor = self.LENGTH ** 2 / (self.ROTATE_THRUSTER_POSITION * 12)
        # Position and velocity
        self.velocity = Vector2()
        self.position = Vector2()
        self.velocity_angular = 0
        self.position_angular = 0
        # Placeholders
        self.engines = {}
        self.fuel_tanks = {}

    def set_position(self, position, position_angular):
        self.position = Vector2(position)
        self.position_angular = position_angular

    def load_image(self, image_filename):
        image = pygame.image.load(image_filename).convert()
        image = pygame.transform.rotozoom(image, -90, self.SCALE_FACTOR)
        return image

    @property
    def rect(self):
        return self.image.get_rect()

    @property
    def status(self):
        speed = self.velocity.length()
        return speed, self.fuel_tanks["primary"].fuel_mass

    @property
    def camera_position(self):
        """Camera position is the coordinate (measured in meters) of the top-left corner of the
        main panel of the display."""
        offset = Vector2(math.copysign(abs(self.velocity.x ** 0.6), self.velocity.x),
                         math.copysign(abs(self.velocity.y ** 0.6), self.velocity.y))
        return self.position - self.panel_center + offset * self.CAMERA_OFFSET_STRENGTH

    @property
    def mass(self):
        fuel_tank_mass = sum([tank.mass for tank in self.fuel_tanks.values()])
        return self.DRY_MASS + fuel_tank_mass

    @property
    def force(self):
        return self.engines["main"].force * self.fuel_tanks["primary"].efficiency

    @property
    def torque(self):
        return ((self.engines["left"].torque - self.engines["right"].torque)
                * self.fuel_tanks["primary"].efficiency)

    def update(self, external_acceleration):
        self._handle_keyboard_input()

        acceleration_angular = (self.torque / (self.mass * self.rotational_inertia_factor)
                                * settings.tick_size * RADIANS_TO_DEGREES)
        self.velocity_angular += acceleration_angular
        self.position_angular += self.velocity_angular * settings.tick_size

        acceleration_magnitude = self.force / self.mass * settings.tick_size
        internal_acceleration = Vector2()
        internal_acceleration.from_polar((acceleration_magnitude, -self.position_angular))
        acceleration = external_acceleration + internal_acceleration
        self.velocity += acceleration
        self.position += self.velocity * settings.tick_size

    def _handle_keyboard_input(self):
        Exception("_handle_Keyboard_input() method not implemented!")

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
        for engine in self.engines.values():
            engine.draw(ship_center, self.position_angular)


class Pegasus(Ship):
    SCALE_FACTOR = 0.6
    DRY_MASS = 1000.0                   # kg
    LENGTH = 2.5                        # m
    ROTATE_THRUSTER_POSITION = 2.0      # m outboard from center of mass
    PRIMARY_BURN_RATE = 4.0             # kg/sec
    PRIMARY_TANK_MASS = 10              # kg
    PRIMARY_TANK_VOLUME = 200           # L

    PARAMETER_LIMITS = {
        "primary_fuel_volume": (0, 200),
        "rotational_burn_rate": (0.15, 1.0)
    }

    def __init__(self, panel, primary_fuel_volume, rotational_burn_rate):
        super().__init__(panel, "images/A5.png")
        self.primary_burn_rate = self.PRIMARY_BURN_RATE
        self.rotational_burn_rate = clamp(rotational_burn_rate,
                                          self.PARAMETER_LIMITS["rotational_burn_rate"])

        self.fuel_tanks = {
            "primary": propulsion.FuelTank(self.PRIMARY_TANK_MASS, self.PRIMARY_TANK_VOLUME,
                                           fuel_volume=primary_fuel_volume)
        }
        exhaust_velocity = self.fuel_tanks["primary"].exhaust_velocity

        self.engines = {
            "main": propulsion.MainEngine(self.panel, self.primary_burn_rate,
                                          exhaust_velocity, -35, 0.4),
            "left": propulsion.RotationEngine(self.panel, self.rotational_burn_rate,
                                              exhaust_velocity, self.ROTATE_THRUSTER_POSITION,
                                              Vector2(15, 10), Vector2(-15, -35), 0.12, LEFT),
            "right": propulsion.RotationEngine(self.panel, self.rotational_burn_rate,
                                               exhaust_velocity, self.ROTATE_THRUSTER_POSITION,
                                               Vector2(15, -10), Vector2(-15, 35), 0.12, RIGHT)
        }

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["primary_fuel_mass"], dict_["rotational_burn_rate"])

    def _handle_keyboard_input(self):
        empty = self.fuel_tanks["primary"].is_empty
        pressed_keys = pygame.key.get_pressed()
        self.engines["main"].update(not empty and pressed_keys[pygame.K_UP])
        self.engines["left"].update(not empty and pressed_keys[pygame.K_LEFT])
        self.engines["right"].update(not empty and pressed_keys[pygame.K_RIGHT])
        burn_mass = sum([engine_.fuel_burn for engine_ in self.engines.values()])
        self.fuel_tanks["primary"].update(burn_mass)


class Manticore(Ship):
    SCALE_FACTOR = 0.6
    DRY_MASS = 1400.0               # kg
    LENGTH = 3.5                    # m
    ROTATE_THRUSTER_POSITION = 2.0  # m outboard from center of mass
    PRIMARY_BURN_RATE = 5.5         # kg/sec
    PRIMARY_TANK_MASS = 50          # kg
    SECONDARY_TANK_MASS = 10        # kg
    PRIMARY_TANK_VOLUME = 500       # L
    SECONDARY_TANK_VOLUME = 50      # L

    PARAMETER_LIMITS = {
        "primary_fuel_mass": (0, 515),
        "secondary_fuel_mass": (0, 14),
        "rotational_burn_rate": (0.2, 2.0),
        "rotational_throttle_ratio": (0.1, 0.5)
    }

    def __init__(self, panel, primary_fuel_volume, secondary_fuel_volume,
                 rotational_burn_rate, rotational_throttle_ratio):
        super().__init__(panel, "images/A6.png")
        self.primary_burn_rate = self.PRIMARY_BURN_RATE
        self.rotational_burn_rate = clamp(rotational_burn_rate,
                                          self.PARAMETER_LIMITS["rotational_burn_rate"])
        self.rotational_throttle_ratio = clamp(rotational_throttle_ratio,
                                               self.PARAMETER_LIMITS["rotational_throttle_ratio"])

        self.fuel_tanks = {
            "primary": propulsion.FuelTank(self.PRIMARY_TANK_MASS, self.PRIMARY_TANK_VOLUME,
                                           "Kerolox", fuel_volume=primary_fuel_volume),
            "secondary": propulsion.FuelTank(self.SECONDARY_TANK_MASS, self.SECONDARY_TANK_VOLUME,
                                             fuel_volume=secondary_fuel_volume)
        }
        primary_exhaust_velocity = self.fuel_tanks["primary"].exhaust_velocity
        secondary_exhaust_velocity = self.fuel_tanks["secondary"].exhaust_velocity

        self.engines = {
            "main": propulsion.MainEngine(self.panel, self.primary_burn_rate,
                                          primary_exhaust_velocity, -45, 0.4),
            "left": propulsion.RotationEngine(self.panel, self.rotational_burn_rate,
                                              secondary_exhaust_velocity,
                                              self.ROTATE_THRUSTER_POSITION,
                                              Vector2(18, 13), Vector2(-15, -25), 0.12, LEFT,
                                              self.rotational_throttle_ratio),
            "right": propulsion.RotationEngine(self.panel, self.rotational_burn_rate,
                                               secondary_exhaust_velocity,
                                               self.ROTATE_THRUSTER_POSITION,
                                               Vector2(18, -13), Vector2(-15, 25), 0.12, RIGHT,
                                               self.rotational_throttle_ratio)
        }

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["primary_fuel_mass"], dict_["secondary_fuel_mass"],
                   dict_["rotational_burn_rate"], dict_["rotational_throttle_ratio"])

    def _handle_keyboard_input(self):
        pressed_keys = pygame.key.get_pressed()
        primary_empty = self.fuel_tanks["primary"].is_empty
        self.engines["main"].update(not primary_empty and pressed_keys[pygame.K_UP])
        self.fuel_tanks["primary"].update(self.engines["main"].fuel_burn)

        secondary_empty = self.fuel_tanks["secondary"].is_empty
        self.engines["left"].update(not secondary_empty and pressed_keys[pygame.K_LEFT],
                                    pressed_keys[pygame.K_LSHIFT])
        self.engines["right"].update(not secondary_empty and pressed_keys[pygame.K_RIGHT],
                                     pressed_keys[pygame.K_LSHIFT])
        self.fuel_tanks["secondary"].update(self.engines["left"].fuel_burn
                                            + self.engines["right"].fuel_burn)
