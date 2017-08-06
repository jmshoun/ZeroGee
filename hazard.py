import pygame
from pygame.math import Vector2

import config

settings = config.DisplaySettings()


class GravityZone(object):
    BACKGROUND_COLOR = (50, 120, 50)
    BORDER_COLOR = (50, 250, 50)
    HATCH_COLOR = (50, 20, 50)
    HATCH_WIDTH = 8
    HATCH_SPACING = 50
    HATCH_SCALE = 3

    def __init__(self, panel, bounding_box, strength, direction):
        self.panel = panel
        min_x, min_y, max_x, max_y = bounding_box
        size = max_x - min_x, max_y - min_y
        self.rect = pygame.Rect(min_x, min_y, *size)
        self.acceleration = Vector2()
        self.acceleration.from_polar((strength, direction))
        self.image = self._render_image()
        self.blit_rect = self.image.get_rect()

    @classmethod
    def from_dict(cls, panel, dict_):
        return cls(panel, dict_["bounding_box"], dict_["strength"], dict_["direction"])

    def _render_image(self):
        image_size = Vector2(self.rect.size) / settings.meters_per_pixel
        image = pygame.Surface(image_size)
        image.fill(self.BACKGROUND_COLOR)
        pygame.draw.rect(image, self.BORDER_COLOR, image.get_rect(), 1)
        image = self._render_hatches(image)
        image.set_alpha(100)
        return image

    def _render_hatches(self, image):
        x = self.HATCH_SPACING / 2
        while x < image.get_rect().width:
            y = self.HATCH_SPACING / 2
            while y < image.get_rect().height:
                image = self._render_hatch(image, x, y)
                y += self.HATCH_SPACING
            x += self.HATCH_SPACING
        return image

    def _render_hatch(self, image, x, y):
        position = Vector2(x, y)
        direction = self.acceleration * self.HATCH_SCALE
        baseline = direction.rotate(90)
        baseline.scale_to_length(self.HATCH_WIDTH)
        tip = position + direction
        left_base, right_base = position + baseline, position - baseline
        pygame.draw.aaline(image, self.HATCH_COLOR, left_base, tip)
        pygame.draw.aaline(image, self.HATCH_COLOR, right_base, tip)
        return image

    def draw(self, camera_position):
        self.blit_rect.topleft = (self.rect.topleft - camera_position) / settings.meters_per_pixel
        self.panel.blit(self.image, self.blit_rect)

    def current_acceleration(self, ship_position):
        if self.rect.collidepoint(*ship_position):
            return self.acceleration * settings.tick_size
        else:
            return Vector2()
