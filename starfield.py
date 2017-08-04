import random

import config


class Starfield(object):
    def __init__(self, panel):
        settings = config.read_config_section(section="starfield")
        self.panel = panel
        width, height = panel.get_size()
        self.stars = []
        for num_stars, parallax_rate, luminosity \
                in zip(settings["num_stars"], settings["parallax_rate"], settings["luminosity"]):
            self.stars += [Star(width, height, luminosity, parallax_rate)
                           for _ in range(num_stars)]

    def draw(self, camera_position):
        for star in self.stars:
            star.draw(camera_position, self.panel)


class Star(object):
    def __init__(self, width, height, luminosity, parallax_rate):
        self.width, self.height = width, height
        self.x, self.y = random.randint(0, width), random.randint(0, height)
        luminosity_max = min(255, luminosity * 3 // 2)
        self.color = tuple([int(random.triangular(luminosity // 2, luminosity_max))
                            for _ in range(3)])
        self.parallax_rate = parallax_rate

    def draw(self, camera_position, panel):
        camera_x, camera_y = camera_position
        render_x, render_y = (int((self.x - camera_x * self.parallax_rate) % self.width),
                              int((self.y - camera_y * self.parallax_rate) % self.height))
        panel.set_at((render_x, render_y), self.color)
