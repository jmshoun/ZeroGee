import pygame
import pygame.freetype

import text


class HUD(object):
    TIME_VERTICAL_OFFSET = 0.0
    WAYPOINT_VERTICAL_OFFSET = 0.27
    SPEED_VERTICAL_OFFSET = 0.6
    FUEL_VERTICAL_OFFSET = 0.8

    def __init__(self, panel):
        self.time = 0
        self.course_status = {}
        self.speed = 0
        self.panel = panel
        self.fuel_mass = None
        self.primary_font = pygame.freetype.Font('fonts/AlphaSmart3000.ttf')
    
    def update(self, time, course_status, ship_status):
        self.time = time
        self.course_status = course_status
        self.speed, self.fuel_mass = ship_status
        self.fuel_mass = max(self.fuel_mass, 0)
    
    def draw(self):
        self._draw_waypoint()
        self._draw_time()
        self._draw_speed()
        self._draw_fuel()

    def _draw_waypoint(self):
        current_gate = self.course_status["current_gate"]
        num_gates = self.course_status["num_gates"]
        current_proxy = self.course_status["current_proxy"]
        num_proxies = self.course_status["num_proxies"]
        waypoint_text = "{0:02d} / {1:02d}".format(current_gate + current_proxy,
                                                   num_gates + num_proxies)
        gate_text = "{0:02d}/{1:02d}".format(current_gate, num_gates) if num_gates > 0 else "--/--"
        proxy_text = "{0:02d}/{1:02d}".format(current_proxy, num_proxies) \
            if num_proxies > 0 else "--/--"

        text.render_text(self.panel, self.primary_font, "Waypoints:",
                         (0.50, self.WAYPOINT_VERTICAL_OFFSET + .04),
                         foreground=text.BLUE, size=1.5, justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, waypoint_text,
                         (0.50, self.WAYPOINT_VERTICAL_OFFSET + 0.14),
                         size=2.5, justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, "Gates:",
                         (0.25, self.WAYPOINT_VERTICAL_OFFSET + 0.22),
                         foreground=text.BLUE, size=0.8, justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, "Proxies:",
                         (0.75, self.WAYPOINT_VERTICAL_OFFSET + 0.22),
                         foreground=text.BLUE, size=0.8, justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, gate_text,
                         (0.25, self.WAYPOINT_VERTICAL_OFFSET + 0.28),
                         size=1.2, justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, proxy_text,
                         (0.75, self.WAYPOINT_VERTICAL_OFFSET + 0.28),
                         size=1.2, justify=text.CENTER)

    def _draw_speed(self):
        speed_text = "{0:>05.2f}".format(self.speed)

        text.render_text(self.panel, self.primary_font, "Velocity:",
                         (0.50, self.SPEED_VERTICAL_OFFSET + 0.03),
                         foreground=text.BLUE, size=1.2, justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, speed_text,
                         (0.40, self.SPEED_VERTICAL_OFFSET + 0.16), size=2.4, justify=text.BOTTOM)
        text.render_text(self.panel, self.primary_font, "m/s",
                         (0.75, self.SPEED_VERTICAL_OFFSET + 0.16), size=1.5, justify=text.BOTTOM,
                         foreground=text.BLUE)

    def _draw_fuel(self):
        fuel_text = "{0:>05.1f}".format(self.fuel_mass)

        text.render_text(self.panel, self.primary_font, "Fuel Left:",
                         (0.50, self.FUEL_VERTICAL_OFFSET + 0.03),
                         foreground=text.BLUE, size=1.2, justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, fuel_text,
                         (0.40, self.FUEL_VERTICAL_OFFSET + 0.16), size=2.4, justify=text.BOTTOM)
        text.render_text(self.panel, self.primary_font, "kg",
                         (0.72, self.FUEL_VERTICAL_OFFSET + 0.16), size=1.5, justify=text.BOTTOM,
                         foreground=text.BLUE)

    def _draw_time(self):
        time_text = self.format_time(self.time)

        text.render_text(self.panel, self.primary_font, time_text,
                         (0.50, self.TIME_VERTICAL_OFFSET + .06),  size=3.0, justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, "Split:",
                         (0.45, self.TIME_VERTICAL_OFFSET + 0.17), foreground=text.BLUE, size=1.0,
                         justify=text.CENTER)
        text.render_text(self.panel, self.primary_font, "00:00.00",
                         (0.95, self.TIME_VERTICAL_OFFSET + 0.17), size=1.0, justify=text.RIGHT)
        text.render_text(self.panel, self.primary_font, "+00:00.00",
                         (0.95, self.TIME_VERTICAL_OFFSET + 0.23), size=1.0, justify=text.RIGHT)

    @staticmethod
    def format_time(time):
        time_minutes = int(time // 60)
        time_seconds = time % 60
        return "{0:02d}:{1:>05.2f}".format(time_minutes, time_seconds)