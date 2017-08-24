import math

import pygame
from pygame.math import Vector2

import config
import propulsion

settings = config.DisplaySettings()
controls = config.Controls()
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
    elif ship_type == "Dragon":
        return Dragon.from_dict(panel, dict_)
    elif ship_type == "Phoenix":
        return Phoenix.from_dict(panel, dict_)
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
        total_force = Vector2(0, 0)
        for engine_ in self.engines.values():
            total_force += engine_.force
        return total_force

    @property
    def torque(self):
        return sum([engine_.torque for engine_ in self.engines.values()])

    def update(self, external_acceleration):
        self._handle_keyboard_input()

        acceleration_angular = (self.torque / (self.mass * self.rotational_inertia_factor)
                                * settings.tick_size * RADIANS_TO_DEGREES)
        self.velocity_angular += acceleration_angular
        self.position_angular += self.velocity_angular * settings.tick_size

        internal_acceleration = self.force / self.mass * settings.tick_size
        internal_acceleration.rotate_ip(-self.position_angular)
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

        def rotational_engine(location, orientation):
            thruster_position = self.ROTATE_THRUSTER_POSITION * (1 if location.x > 0 else -1)
            return propulsion.Engine(self.panel, self.rotational_burn_rate,
                                     self.fuel_tanks["primary"], location, 0.12, orientation,
                                     thruster_position)

        self.engines = {
            "main": propulsion.Engine(self.panel, self.primary_burn_rate,
                                      self.fuel_tanks["primary"], Vector2(-35, 0), 0.4,
                                      direction=0),
            "left_fore": rotational_engine(Vector2(15, 10), 90),
            "left_aft": rotational_engine(Vector2(-15, 35), 90),
            "right_fore": rotational_engine(Vector2(15, -10), -90),
            "right_aft": rotational_engine(Vector2(-15, -35), -90)
        }

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["primary_fuel_volume"], dict_["rotational_burn_rate"])

    def _handle_keyboard_input(self):
        pressed_keys = pygame.key.get_pressed()
        forward = pressed_keys[controls.forward]
        left = pressed_keys[controls.left]
        right = pressed_keys[controls.right]

        empty = self.fuel_tanks["primary"].is_empty
        self.engines["main"].update(forward and not empty)
        self.engines["left_fore"].update(left and not empty)
        self.engines["right_aft"].update(left and not empty)
        self.engines["right_fore"].update(right and not empty)
        self.engines["left_aft"].update(right and not empty)
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
        "rotational_burn_rate": (0.2, 2.0),
        "rotational_throttle_ratio": (0.1, 0.5)
    }

    FUEL_TANK_OPTIONS = {
        "Small": {"mass": 25, "volume": 200},
        "Medium": {"mass": 40, "volume": 500}
    }

    def __init__(self, panel, primary_fuel_volume, secondary_fuel_volume, primary_fuel_tank_size,
                 rotational_burn_rate, rotational_throttle_ratio):
        super().__init__(panel, "images/A6.png")
        self.primary_burn_rate = self.PRIMARY_BURN_RATE
        self.rotational_burn_rate = clamp(rotational_burn_rate,
                                          self.PARAMETER_LIMITS["rotational_burn_rate"])
        self.rotational_throttle_ratio = clamp(rotational_throttle_ratio,
                                               self.PARAMETER_LIMITS["rotational_throttle_ratio"])
        primary_fuel_tank_size = primary_fuel_tank_size  \
            if primary_fuel_tank_size in self.FUEL_TANK_OPTIONS.keys() else "Medium"

        primary_tank_mass = self.FUEL_TANK_OPTIONS[primary_fuel_tank_size]["mass"]
        primary_tank_volume = self.FUEL_TANK_OPTIONS[primary_fuel_tank_size]["volume"]
        self.fuel_tanks = {
            "primary": propulsion.FuelTank(primary_tank_mass, primary_tank_volume,
                                           "Kerolox", fuel_volume=primary_fuel_volume),
            "secondary": propulsion.FuelTank(self.SECONDARY_TANK_MASS, self.SECONDARY_TANK_VOLUME,
                                             fuel_volume=secondary_fuel_volume)
        }

        def rotational_engine(location, orientation):
            thruster_position = self.ROTATE_THRUSTER_POSITION * (1 if location.x > 0 else -1)
            return propulsion.Engine(self.panel, self.rotational_burn_rate,
                                     self.fuel_tanks["secondary"], location, 0.12, orientation,
                                     thruster_position, self.rotational_throttle_ratio)

        self.engines = {
            "main": propulsion.Engine(self.panel, self.primary_burn_rate,
                                      self.fuel_tanks["primary"], Vector2(-45, 0), 0.4,
                                      direction=0),
            "left_fore": rotational_engine(Vector2(18, 13), 90),
            "left_aft": rotational_engine(Vector2(-15, 25), 90),
            "right_fore": rotational_engine(Vector2(18, -13), -90),
            "right_aft": rotational_engine(Vector2(-15, -25), -90)
        }

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["primary_fuel_volume"], dict_["secondary_fuel_volume"],
                   dict_["primary_fuel_tank_size"], dict_["rotational_burn_rate"],
                   dict_["rotational_throttle_ratio"])

    def _handle_keyboard_input(self):
        pressed_keys = pygame.key.get_pressed()
        forward = pressed_keys[controls.forward]
        left = pressed_keys[controls.left]
        right = pressed_keys[controls.right]
        rotational_throttle = pressed_keys[controls.rotational_throttle]

        primary_empty = self.fuel_tanks["primary"].is_empty
        self.engines["main"].update(forward and not primary_empty)
        self.fuel_tanks["primary"].update(self.engines["main"].fuel_burn)

        secondary_empty = self.fuel_tanks["secondary"].is_empty
        self.engines["left_fore"].update(left and not secondary_empty, rotational_throttle)
        self.engines["right_aft"].update(left and not secondary_empty, rotational_throttle)
        self.engines["right_fore"].update(right and not secondary_empty, rotational_throttle)
        self.engines["left_aft"].update(right and not secondary_empty, rotational_throttle)
        secondary_burn_mass = sum([engine_.fuel_burn for name, engine_ in self.engines.items()
                                   if name != "main"])
        self.fuel_tanks["secondary"].update(secondary_burn_mass)


class Dragon(Ship):
    SCALE_FACTOR = 0.6
    DRY_MASS = 2100.0  # kg
    LENGTH = 4.0  # m
    ROTATE_THRUSTER_POSITION = 2.0  # m outboard from center of mass
    PRIMARY_BURN_RATE = 6.0         # kg/sec
    PRIMARY_TANK_MASS = 100         # kg
    SECONDARY_TANK_MASS = 20        # kg
    PRIMARY_TANK_VOLUME = 2000      # L
    SECONDARY_TANK_VOLUME = 150     # L

    PARAMETER_LIMITS = {
        "rotational_burn_rate": (0.2, 2.0),
        "rotational_throttle_ratio": (0.1, 0.5),
        "primary_fuel_type": ["HydroFlouro", "Kerolox"]
    }

    def __init__(self, panel, primary_fuel_volume, secondary_fuel_volume, primary_fuel_type,
                 rotational_burn_rate, rotational_throttle_ratio):
        super().__init__(panel, "images/A7.png")
        self.primary_burn_rate = self.PRIMARY_BURN_RATE
        self.rotational_burn_rate = clamp(rotational_burn_rate,
                                          self.PARAMETER_LIMITS["rotational_burn_rate"])
        self.rotational_throttle_ratio = clamp(rotational_throttle_ratio,
                                               self.PARAMETER_LIMITS["rotational_throttle_ratio"])
        primary_fuel_type = primary_fuel_type \
            if primary_fuel_type in self.PARAMETER_LIMITS["primary_fuel_type"] else "Kerolox"

        self.fuel_tanks = {
            "primary": propulsion.FuelTank(self.PRIMARY_TANK_MASS, self.PRIMARY_TANK_VOLUME,
                                           primary_fuel_type, fuel_volume=primary_fuel_volume),
            "secondary": propulsion.FuelTank(self.SECONDARY_TANK_MASS, self.SECONDARY_TANK_VOLUME,
                                             fuel_volume=secondary_fuel_volume)
        }

        def rotational_engine(location, orientation):
            thruster_position = self.ROTATE_THRUSTER_POSITION * (1 if location.x > 0 else -1)
            return propulsion.Engine(self.panel, self.rotational_burn_rate,
                                     self.fuel_tanks["secondary"], location, 0.12, orientation,
                                     thruster_position, self.rotational_throttle_ratio)

        self.engines = {
            "main": propulsion.Engine(self.panel, self.primary_burn_rate,
                                      self.fuel_tanks["primary"], Vector2(-45, 0), 0.4,
                                      direction=0),
            "left_fore": rotational_engine(Vector2(15, 26), 90),
            "left_aft": rotational_engine(Vector2(-20, 32), 90),
            "right_fore": rotational_engine(Vector2(15, -26), -90),
            "right_aft": rotational_engine(Vector2(-20, -32), -90)
        }

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["primary_fuel_volume"], dict_["secondary_fuel_volume"],
                   dict_["primary_fuel_type"], dict_["rotational_burn_rate"],
                   dict_["rotational_throttle_ratio"])

    def _handle_keyboard_input(self):
        pressed_keys = pygame.key.get_pressed()
        forward = pressed_keys[controls.forward]
        left = pressed_keys[controls.left]
        right = pressed_keys[controls.right]
        left_slew = pressed_keys[controls.left_slew]
        right_slew = pressed_keys[controls.right_slew]
        rotational_throttle = pressed_keys[controls.rotational_throttle]

        primary_empty = self.fuel_tanks["primary"].is_empty
        self.engines["main"].update(forward and not primary_empty)
        self.fuel_tanks["primary"].update(self.engines["main"].fuel_burn)

        secondary_empty = self.fuel_tanks["secondary"].is_empty
        self.engines["left_fore"].update((left or left_slew) and not secondary_empty,
                                         rotational_throttle)
        self.engines["right_aft"].update((left or right_slew) and not secondary_empty,
                                         rotational_throttle)
        self.engines["right_fore"].update((right or right_slew) and not secondary_empty,
                                          rotational_throttle)
        self.engines["left_aft"].update((right or left_slew) and not secondary_empty,
                                        rotational_throttle)

        secondary_burn_mass = sum([engine_.fuel_burn for name, engine_ in self.engines.items()
                                   if name != "main"])
        self.fuel_tanks["secondary"].update(secondary_burn_mass)


class Phoenix(Ship):
    SCALE_FACTOR = 0.7
    DRY_MASS = 1500.0               # kg
    LENGTH = 3.5                    # m
    ROTATE_THRUSTER_POSITION = 2.0  # m outboard from center of mass
    PRIMARY_BURN_RATE = 7.0         # kg/sec
    PRIMARY_TANK_MASS = 100         # kg
    SECONDARY_TANK_MASS = 20        # kg
    PRIMARY_TANK_VOLUME = 2000      # L
    SECONDARY_TANK_VOLUME = 150     # L

    PARAMETER_LIMITS = {
        "rotational_burn_rate": (0.2, 2.0),
        "rotational_throttle_ratio": (0.1, 0.5),
        "primary_fuel_type": ["ChloroFlouro", "HydroFlouro", "Kerolox", "hydroBeryllox"],
        "nose_burn_rate": (1.0, 10.0)
    }

    def __init__(self, panel, primary_fuel_volume, secondary_fuel_volume, primary_fuel_type,
                 rotational_burn_rate, rotational_throttle_ratio, nose_burn_rate):
        super().__init__(panel, "images/A10.png")
        self.primary_burn_rate = self.PRIMARY_BURN_RATE
        self.nose_burn_rate = nose_burn_rate
        self.rotational_burn_rate = clamp(rotational_burn_rate,
                                          self.PARAMETER_LIMITS["rotational_burn_rate"])
        self.rotational_throttle_ratio = clamp(rotational_throttle_ratio,
                                               self.PARAMETER_LIMITS["rotational_throttle_ratio"])
        primary_fuel_type = primary_fuel_type \
            if primary_fuel_type in self.PARAMETER_LIMITS["primary_fuel_type"] else "Kerolox"

        self.fuel_tanks = {
            "primary": propulsion.FuelTank(self.PRIMARY_TANK_MASS, self.PRIMARY_TANK_VOLUME,
                                           primary_fuel_type, fuel_volume=primary_fuel_volume),
            "secondary": propulsion.FuelTank(self.SECONDARY_TANK_MASS, self.SECONDARY_TANK_VOLUME,
                                             fuel_volume=secondary_fuel_volume)
        }

        def rotational_engine(location, orientation):
            thruster_position = self.ROTATE_THRUSTER_POSITION * (1 if location.x > 0 else -1)
            return propulsion.Engine(self.panel, self.rotational_burn_rate,
                                     self.fuel_tanks["secondary"], location, 0.12, orientation,
                                     thruster_position, self.rotational_throttle_ratio)

        self.engines = {
            "main": propulsion.Engine(self.panel, self.primary_burn_rate,
                                      self.fuel_tanks["primary"], Vector2(-40, 0), 0.4,
                                      direction=0),
            "nose": propulsion.Engine(self.panel, self.nose_burn_rate,
                                      self.fuel_tanks["secondary"], Vector2(40, 0), 0.25,
                                      direction=180),
            "left_fore": rotational_engine(Vector2(20, 12), 90),
            "left_aft": rotational_engine(Vector2(-20, 32), 90),
            "right_fore": rotational_engine(Vector2(20, -12), -90),
            "right_aft": rotational_engine(Vector2(-20, -32), -90)
        }

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["primary_fuel_volume"], dict_["secondary_fuel_volume"],
                   dict_["primary_fuel_type"], dict_["rotational_burn_rate"],
                   dict_["rotational_throttle_ratio"], dict_["nose_burn_rate"])

    def _handle_keyboard_input(self):
        pressed_keys = pygame.key.get_pressed()
        forward = pressed_keys[controls.forward]
        nose = pressed_keys[controls.nose]
        left = pressed_keys[controls.left]
        right = pressed_keys[controls.right]
        left_slew = pressed_keys[controls.left_slew]
        right_slew = pressed_keys[controls.right_slew]
        rotational_throttle = pressed_keys[controls.rotational_throttle]

        primary_empty = self.fuel_tanks["primary"].is_empty
        self.engines["main"].update(forward and not primary_empty)
        self.fuel_tanks["primary"].update(self.engines["main"].fuel_burn)

        secondary_empty = self.fuel_tanks["secondary"].is_empty
        self.engines["left_fore"].update((left or left_slew) and not secondary_empty,
                                         rotational_throttle)
        self.engines["right_aft"].update((left or right_slew) and not secondary_empty,
                                         rotational_throttle)
        self.engines["right_fore"].update((right or right_slew) and not secondary_empty,
                                          rotational_throttle)
        self.engines["left_aft"].update((right or left_slew) and not secondary_empty,
                                        rotational_throttle)
        self.engines["nose"].update(nose and not secondary_empty)

        secondary_burn_mass = sum([engine_.fuel_burn for name, engine_ in self.engines.items()
                                   if name != "main"])
        self.fuel_tanks["secondary"].update(secondary_burn_mass)
