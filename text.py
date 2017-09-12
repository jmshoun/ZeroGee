import pygame

import config

settings = config.DisplaySettings()

FONT_SIZE_LOOKUP = {
    (1360, 768): 24,
    (1920, 1080): 32
}

reference_font_size = FONT_SIZE_LOOKUP[settings.screen_resolution]

TOP_LEFT = (0, 0)
TOP = (0.5, 0.0)
CENTER = (0.5, 0.5)
BOTTOM = (0.5, 1.0)
RIGHT = (1.0, 0.5)
LEFT = (0.0, 0.5)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


def render_text(surface, font, text, location, foreground=WHITE, background=BLACK,
                size=1, justify=TOP_LEFT):
    size_px = reference_font_size * size
    surface_size = surface.get_size()
    location_px = (location[0] * surface_size[0],
                   location[1] * surface_size[1])

    pad_width = font.get_rect("/", size=size_px).width
    raw_surface, raw_rect = font.render("/" + text + "/", foreground, background, size=size_px)
    text_surface = raw_surface.subsurface(pygame.Rect(pad_width, 0,
                                                      raw_rect.width - 2 * pad_width,
                                                      raw_rect.height))
    text_rect = text_surface.get_rect()
    location_offset = (text_rect.width * justify[0], text_rect.height * justify[1])
    location_px = (location_px[0] - location_offset[0], location_px[1] - location_offset[1])
    surface.blit(text_surface, location_px)
