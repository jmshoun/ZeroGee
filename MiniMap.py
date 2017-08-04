import pygame
from pygame.math import Vector2


class MiniMap(object):
    PANEL_MARGIN_PX = 10
    GATE_COLOR = (100, 200, 100)
    PROXY_COLOR = (200, 100, 100)
    FINISH_BOX_COLOR = (200, 100, 200)
    GRAVITY_ZONE_COLOR = (50, 100, 50)
    SHIP_COLOR = (100, 100, 255)
    PROXY_RADIUS = 1
    GATE_RADIUS = 2
    SHIP_RADIUS = 3
    FINISH_BOX_SIZE = 4

    def __init__(self, panel, course, ship):
        self.panel = panel
        self.course = course
        self.ship = ship

        min_x, max_x, min_y, max_y = self.course.bounding_box
        x_range, y_range = max_x - min_x, max_y - min_y
        panel_size = Vector2(self.panel.get_size())

        self.meters_per_pixel = max(x_range / (panel_size.x - 2 * self.PANEL_MARGIN_PX),
                                    y_range / (panel_size.y - 2 * self.PANEL_MARGIN_PX))
        self.finish_box_size = Vector2(self.FINISH_BOX_SIZE, self.FINISH_BOX_SIZE)
        center = Vector2(min_x + x_range / 2, min_y + y_range / 2)
        self.origin = center - panel_size / 2 * self.meters_per_pixel

    def draw(self):
        for gate in self.course.gates:
            self._draw_gate(gate)
        for proxy in self.course.proxies:
            self._draw_proxy(proxy)
        for zone in self.course.gravity_zones:
            self._draw_gravity_zone(zone)
        self._draw_finish_box()
        self._draw_ship()

    def _draw_gate(self, gate):
        position = self._position_to_pixels(gate.position)
        pygame.draw.circle(self.panel, self.GATE_COLOR, position, self.GATE_RADIUS)

    def _draw_proxy(self, proxy):
        position = self._position_to_pixels(proxy.position)
        pygame.draw.circle(self.panel, self.PROXY_COLOR, position, self.PROXY_RADIUS)

    def _draw_gravity_zone(self, zone):
        top_left = self._position_to_pixels(Vector2(zone.rect.topleft))
        size = Vector2(zone.rect.size) / self.meters_per_pixel
        rect = pygame.Rect(*top_left, size.x, size.y)
        pygame.draw.rect(self.panel, self.GRAVITY_ZONE_COLOR, rect)

    def _draw_finish_box(self):
        position = self._position_to_pixels(self.course.finish_box.position)
        finish_rect = pygame.Rect(*(Vector2(position) - self.finish_box_size / 2),
                                  self.FINISH_BOX_SIZE, self.FINISH_BOX_SIZE)
        pygame.draw.rect(self.panel, self.FINISH_BOX_COLOR, finish_rect)

    def _draw_ship(self):
        position = self._position_to_pixels(self.ship.position)
        pygame.draw.circle(self.panel, self.SHIP_COLOR, position, self.SHIP_RADIUS)

    def _position_to_pixels(self, position):
        pixels = (position - self.origin) / self.meters_per_pixel
        return int(pixels.x), int(pixels.y)