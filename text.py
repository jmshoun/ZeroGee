import config

settings = config.DisplaySettings()

FONT_SIZE_LOOKUP = {
    (1360, 768): 24
}

reference_font_size = FONT_SIZE_LOOKUP[settings.screen_resolution]

TOP_LEFT = (0, 0)
CENTER = (0.5, 0.5)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)


def render_text(surface, font, text, location, foreground=WHITE, background=BLACK,
                size=1, justify=TOP_LEFT):
    size_px = reference_font_size * size
    surface_size = surface.get_size()
    location_px = (location[0] * surface_size[0],
                   location[1] * surface_size[1])

    if justify == TOP_LEFT:
        font.render_to(surface, location_px, text, fgcolor=foreground, bgcolor=background,
                       size=size_px)
    else:
        text_surface = font.render(text, foreground, background, size=size_px)
        text_size = text_surface.get_size()
        location_offset = (text_size[0] * justify[0], text_size[1] * justify[1])
        location_px = (location_px[0] - location_offset[0], location_px[1] - location_offset[1])
        surface.blit(text_surface, location_px)
