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
        self.finish_box_size = Vector2(self.FINISH_BOX_SIZE, self.FINISH_BOX_SIZE)
        self.bounding_rect = self.course.bounding_rect
        self.default_origin, self.default_meters_per_pixel = \
            self.translation_factors(self.bounding_rect)
        self.origin, self.meters_per_pixel = self.default_origin, self.default_meters_per_pixel

    def translation_factors(self, bounding_rect):
        width, height = bounding_rect.size
        panel_size = Vector2(self.panel.get_size())
        meters_per_pixel = max(width / (panel_size.x - 2 * self.PANEL_MARGIN_PX),
                               height / (panel_size.y - 2 * self.PANEL_MARGIN_PX))
        center = Vector2(bounding_rect.left + width / 2, bounding_rect.top + height / 2)
        origin = center - panel_size / 2 * meters_per_pixel
        return origin, meters_per_pixel

    def inflate_bounding_box(self, ship_position):
        rect = self.bounding_rect
        if ship_position.x < rect.left:
            rect = pygame.Rect(ship_position.x, rect.top, rect.right - ship_position.x, rect.height)
        elif ship_position.x > rect.right:
            rect = pygame.Rect(rect.left, rect.top, ship_position.x - rect.left, rect.height)
        if ship_position.y < rect.top:
            rect = pygame.Rect(rect.left, ship_position.y, rect.width,
                               rect.bottom - ship_position.y)
        elif ship_position.y > rect.bottom:
            rect = pygame.Rect(rect.left, rect.top, rect.width, ship_position.y - rect.top)
        return rect

    def set_translation_factors(self):
        if self.bounding_rect.collidepoint(*self.ship.position):
            self.origin = self.default_origin
            self.meters_per_pixel = self.default_meters_per_pixel
        else:
            bounding_box = self.inflate_bounding_box(self.ship.position)
            self.origin, self.meters_per_pixel = self.translation_factors(bounding_box)

    def draw(self):
        self.set_translation_factors()
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
