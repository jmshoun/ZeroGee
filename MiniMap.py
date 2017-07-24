import pygame


class MiniMap(object):
    PANEL_MARGIN_PX = 10
    GATE_COLOR = (100, 200, 100)
    FINISH_BOX_COLOR = (200, 100, 200)
    SHIP_COLOR = (100, 100, 255)
    GATE_RADIUS = 2
    SHIP_RADIUS = 3
    FINISH_BOX_SIZE = 4

    def __init__(self, panel, course, ship):
        self.panel = panel
        self.course = course
        self.ship = ship

        min_x, max_x, min_y, max_y = self.course.bounding_box()
        x_range, y_range = max_x - min_x, max_y - min_y
        panel_px_x, panel_px_y = self.panel.get_size()

        self.meters_per_pixel = max(x_range / (panel_px_x - 2 * self.PANEL_MARGIN_PX),
                                    y_range / (panel_px_y - 2 * self.PANEL_MARGIN_PX))
        center_x, center_y = min_x + x_range / 2, min_y + y_range / 2
        self.origin_x, self.origin_y = (center_x - panel_px_x / 2 * self.meters_per_pixel,
                                        center_y - panel_px_y / 2 * self.meters_per_pixel)

    def draw(self):
        for gate in self.course.gates:
            self._draw_gate(gate)
        self._draw_finish_box()
        self._draw_ship()

    def _draw_gate(self, gate):
        position = self._position_to_pixels(gate.position_x, gate.position_y)
        pygame.draw.circle(self.panel, self.GATE_COLOR, position, self.GATE_RADIUS)

    def _draw_finish_box(self):
        position_x, position_y = self._position_to_pixels(self.course.finish_box.position_x,
                                                          self.course.finish_box.position_y)
        finish_rect = pygame.Rect(position_x - self.FINISH_BOX_SIZE / 2,
                                  position_y - self.FINISH_BOX_SIZE / 2,
                                  self.FINISH_BOX_SIZE, self.FINISH_BOX_SIZE)
        pygame.draw.rect(self.panel, self.FINISH_BOX_COLOR, finish_rect)

    def _draw_ship(self):
        position = self._position_to_pixels(self.ship.position_x, self.ship.position_y)
        pygame.draw.circle(self.panel, self.SHIP_COLOR, position, self.SHIP_RADIUS)

    def _position_to_pixels(self, position_x, position_y):
        return (int((position_x - self.origin_x) / self.meters_per_pixel),
                int((position_y - self.origin_y) / self.meters_per_pixel))
