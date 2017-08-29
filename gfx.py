import config

settings = config.DisplaySettings()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Sprite(object):
    def __init__(self, panel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.panel = panel
        self.panel_rect = self.panel.get_rect()

    @property
    def image(self):
        raise Exception("image property not defined!")

    def draw(self, **kwargs):
        raise Exception("draw method not defined!")


class LevelSprite(Sprite):
    def __init__(self, panel, *args, **kwargs):
        super().__init__(panel, *args, **kwargs)
        self.blit_rect = None
        self.position = None

    def draw(self, camera_position):
        self.blit_rect.center = (self.position - camera_position) / settings.meters_per_pixel
        self.panel.blit(self.image, self.blit_rect)
