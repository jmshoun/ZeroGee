import pygame
import yaml


def read_config_section(section, filename="config.yaml"):
    with open(filename, "r") as file:
        config = yaml.load(file)
    return config[section]


class DisplaySettings(object):
    def __init__(self, filename="config.yaml"):
        config = read_config_section("display", filename)
        self.screen_resolution = tuple(config["screen_resolution"])
        self.tick_size = config["tick_size"]
        self.scale_factor = config["scale_factor"]
        self.meters_per_pixel = config["meters_per_pixel"] * self.scale_factor


class Controls(object):
    def __init__(self, filename="config.yaml"):
        config = read_config_section("controls", filename)
        self.forward = getattr(pygame, config["forward"])
        self.left = getattr(pygame, config["left"])
        self.right = getattr(pygame, config["right"])
        self.left_slew = getattr(pygame, config["left_slew"])
        self.right_slew = getattr(pygame, config["right_slew"])
        self.rotational_throttle = getattr(pygame, config["rotational_throttle"])
