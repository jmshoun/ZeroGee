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

