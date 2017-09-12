import string
import math

import pygame
import pygame.freetype
import PIL.Image
import PIL.ImageFilter
import PIL.ImageEnhance

import text
import ship


class ShipConfigurator(object):
    DEFAULT_CONFIGURATION_LIMITS = {
        "fuel_type": {"option_width": 0.4, "col_wrap": 2},
        "primary_fuel_volume": {"low": 0},
        "primary_tank_size": {"option_width": 0.15},
        "secondary_fuel_volume": {"low": 0},
        "secondary_tank_size": {},
        "rotational_burn_rate": {},
        "rotational_throttle_ratio": {"high": 1.0},
        "slew_burn_rate": {},
        "nose_burn_rate": {},
        "afterburner_throttle_ratio": {"low": 1.0},
        "rotational_assist": {"options": ["On", "Off"], "option_width": 0.3},
        "rotational_velocity": {},
        "position_homing": {"options": ["On", "Off"], "option_width": 0.3}
    }

    TOGGLE_OPTIONS = ["fuel_type", "primary_tank_size", "secondary_tank_size",
                      "rotational_assist", "position_homing"]

    def __init__(self, screen, ship_class):
        self.ship_class = ship_class
        ship_class_limits = getattr(ship, ship_class).CONFIGURATION_LIMITS
        configuration_limits = {k: {**v, **ship_class_limits.get(k, {})}
                                for k, v in self.DEFAULT_CONFIGURATION_LIMITS.items()}
        widgets = []
        for widget_name, params in configuration_limits.items():
            widget_class = Toggle if widget_name in self.TOGGLE_OPTIONS else Slider
            widgets += [widget_class(widget_name, **params)]
        self.widget_group = WidgetGroup(screen, *widgets)
        self.ship_performance = ShipPerformance(screen.subsurface(pygame.Rect(1440, 0, 480, 1080)))

    def draw(self):
        self.widget_group.draw()
        self.ship_performance.draw()

    def update(self):
        ship_ = getattr(ship, self.ship_class)(**self.configuration)
        self.widget_group.update()
        self.ship_performance.update(ship_)

    @property
    def configuration(self):
        return self.widget_group.configuration


class ShipPerformance(object):
    PARAMETER_LOCATIONS = {
        "mass": {"position": (0.5, 0.1), "places": 1},
        "dry_mass": {"position": (0.8, 0.1), "places": 1}
    }

    def __init__(self, panel, ship_=None):
        self.panel = panel
        self.font = pygame.freetype.Font('fonts/larabiefont.ttf')
        self.ship_ = ship_

    def draw(self):
        self.panel.fill((0, 0, 0))
        self._draw_labels()
        if self.ship is None:
            return
        for name, attributes in self.PARAMETER_LOCATIONS.items():
            value = getattr(self.ship, name)
            format_text = "{:0." + str(attributes["places"]) + "f}"
            value_text = format_text.format(value)
            text.render_text(self.panel, self.font, value_text,
                             attributes["position"], justify=text.RIGHT, size=0.7)

    def _draw_labels(self):
        # Draw column headers
        text.render_text(self.panel, self.font, "Wet", (0.5, 0.05), justify=text.RIGHT, size=0.7,
                         foreground=text.GREEN)
        text.render_text(self.panel, self.font, "Dry", (0.8, 0.05), justify=text.RIGHT, size=0.7,
                         foreground=text.GREEN)

        # Draw row labels
        text.render_text(self.panel, self.font, "Mass", (0.1, 0.1), justify=text.LEFT, size=0.7,
                         foreground=text.GREEN)

    def update(self, ship_=None):
        if ship_ is not None:
            self.ship = ship_


class WidgetGroup(object):
    WIDGET_LOCATIONS = {
        "fuel_type": (0.0, 0.0, 0.25, 0.2),
        "primary_fuel_volume": (0.0, 0.2, 0.25, 0.4),
        "primary_tank_size": (0.0, 0.4, 0.25, 0.6),
        "secondary_fuel_volume": (0.0, 0.6, 0.25, 0.8),
        "secondary_tank_size": (0.0, 0.8, 0.25, 1.0),
        "rotational_burn_rate": (0.25, 0.0, 0.5, 0.2),
        "rotational_throttle_ratio": (0.25, 0.2, 0.5, 0.4),
        "slew_burn_rate": (0.25, 0.4, 0.5, 0.6),
        "nose_burn_rate": (0.25, 0.6, 0.5, 0.8),
        "afterburner_throttle_ratio": (0.25, 0.8, 0.5, 1.0),
        "rotational_assist": (0.5, 0.0, 0.75, 0.35),
        "rotational_velocity": (0.5, 0.35, 0.75, 0.65),
        "position_homing": (0.5, 0.65, 0.75, 1.0)
    }

    def __init__(self, screen, *args):
        self.widgets = []
        self.screen_rect = screen.get_rect()
        for widget in args:
            panel_spec = self.WIDGET_LOCATIONS[widget.attribute_name]
            panel_rect = pygame.Rect(panel_spec[0] * self.screen_rect.width,
                                     panel_spec[1] * self.screen_rect.height,
                                     (panel_spec[2] - panel_spec[0]) * self.screen_rect.width,
                                     (panel_spec[3] - panel_spec[1]) * self.screen_rect.height)
            panel = screen.subsurface(panel_rect)
            widget.init_panel(panel)
            self.widgets += [widget]
        self.widgets[0].highlighted = True

    def draw(self):
        for widget in self.widgets:
            widget.draw()

    def update(self):
        highlighted_widget = [widget for widget in self.widgets if widget.highlighted][0]
        key_events = [(e.type, e.key) for e in pygame.event.get()
                      if e.type in [pygame.KEYDOWN, pygame.KEYUP]]

        rect = highlighted_widget.global_rect
        active_point = None
        if (pygame.KEYDOWN, pygame.K_UP) in key_events and rect.top > 0:
            active_point = (rect.left, rect.top - 5)
        elif ((pygame.KEYDOWN, pygame.K_DOWN) in key_events
              and rect.bottom + 5 < self.screen_rect.height):
            active_point = (rect.left, rect.bottom + 5)
        elif (pygame.KEYDOWN, pygame.K_LEFT) in key_events and rect.left > 0:
            active_point = (rect.left - 5, rect.top)
        elif ((pygame.KEYDOWN, pygame.K_RIGHT) in key_events
              and rect.right + 5 < self.screen_rect.width):
            active_point = (rect.right + 5, rect.top)

        if active_point:
            for i, w in enumerate(self.widgets):
                self.widgets[i].highlighted = w.global_rect.collidepoint(active_point)

        for widget in self.widgets:
            widget.update(key_events)

    @property
    def configuration(self):
        return {widget.attribute_name: widget.value for widget in self.widgets
                if not widget.locked}


class Widget(object):
    border_width = 3
    border_standard_color = (50, 120, 50)
    border_highlight_color = (200, 255, 200)

    def __init__(self, attribute_name, locked=False, display_name=None):
        self.font = pygame.freetype.Font('fonts/larabiefont.ttf')
        self.frame = self.panel = None
        self.local_rect = self.global_rect = None
        self.locked = locked
        self.value = None
        self.attribute_name = attribute_name
        self.display_name = display_name if display_name else self.default_display_name
        self.highlighted = False

    def init_panel(self, panel):
        self.frame = panel
        frame_rect = self.frame.get_rect()
        panel_rect = pygame.Rect(self.border_width, self.border_width,
                                 frame_rect.width - 2 * self.border_width,
                                 frame_rect.height - 2 * self.border_width)
        self.panel = self.frame.subsurface(panel_rect)
        self.local_rect = self.panel.get_rect()
        offset = self.frame.get_offset()
        self.global_rect = pygame.Rect(*offset, *frame_rect.size)
        if self.locked:
            self.draw(override_lock=True)
            self.blur()

    def draw(self, override_lock=False):
        border_color = (self.border_highlight_color if self.highlighted
                        else self.border_standard_color)
        pygame.draw.rect(self.frame, border_color, self.frame.get_rect(), self.border_width)
        if override_lock or not self.locked:
            self.panel.fill(text.BLACK)
            text.render_text(self.panel, self.font, self.display_name, (0.5, 0.15), size=0.8,
                             justify=text.TOP)

    def blur(self, blur_size=6):
        image_string = pygame.image.tostring(self.panel, "RGBA")
        image = PIL.Image.frombytes("RGBA", self.panel.get_size(), image_string)
        image = image.filter(PIL.ImageFilter.GaussianBlur(blur_size))
        image = PIL.ImageEnhance.Brightness(image).enhance(0.5)
        blurred_panel = pygame.image.frombuffer(image.tobytes(), image.size, "RGBA")
        self.panel.blit(blurred_panel, (0, 0))

    @property
    def default_display_name(self):
        words = self.attribute_name.split("_")
        cap_words = [string.capwords(word) for word in words]
        return " ".join(cap_words)


class Toggle(Widget):
    option_center = 0.65
    background_color = (20, 20, 60)
    foreground_color = (50, 50, 180)
    edge_color = (150, 150, 150)
    edge_width = 1

    def __init__(self, attribute_name, options=None, value=None, option_width=0.2,
                 col_wrap=None, option_height=0.3, display_name=None):
        locked = options is None or value is None
        super().__init__(attribute_name, locked, display_name)
        self.options = options or ["On", "Off"]
        self.value = value or self.options[0]
        self.current_index = [i for i, e in enumerate(self.options) if e == self.value][0]
        self.option_width = option_width
        self.col_wrap = col_wrap
        self.option_height = option_height

    def update(self, key_events):
        if self.highlighted and not self.locked:
            self._handle_input(key_events)
        self.value = self.options[self.current_index]

    def _handle_input(self, key_events):
        if ((pygame.KEYDOWN, pygame.K_PERIOD) in key_events
                and self.current_index + 1 < len(self.options)):
            self.current_index += 1
        if (pygame.KEYDOWN, pygame.K_COMMA) in key_events and self.current_index > 0:
            self.current_index -= 1

    def draw(self, override_lock=False):
        super().draw(override_lock)
        if self.locked and not override_lock:
            return

        num_rows = math.ceil(len(self.options) / self.col_wrap) if self.col_wrap else 1
        num_cols = self.col_wrap or len(self.options)
        top = self.option_center - num_rows * self.option_height / 2
        starting_left = 0.5 - num_cols * self.option_width / 2
        left = starting_left

        for i, opt in enumerate(self.options):
            self.draw_cell(opt, top, left, opt == self.value)
            left += self.option_width
            if not (i + 1) % num_cols:
                left = starting_left
                top += self.option_height

    def draw_cell(self, name, top, left, selected):
        panel_rect = self.panel.get_rect()
        left_px = panel_rect.width * left
        top_px = panel_rect.height * top
        width_px = panel_rect.width * self.option_width
        height_px = panel_rect.height * self.option_height

        cell_panel = self.panel.subsurface(pygame.Rect(left_px, top_px, width_px, height_px))
        fill_color = self.foreground_color if selected else self.background_color
        cell_panel.fill(fill_color)
        pygame.draw.rect(cell_panel, self.edge_color, cell_panel.get_rect(), self.edge_width)
        text.render_text(cell_panel, self.font, name, (0.5, 0.5), background=fill_color,
                         size=0.5, justify=text.CENTER)


class Slider(Widget):
    margin_horizontal = 0.1
    line_color = (100, 200, 100)
    line_width = 4
    repeat_first_delay = 15
    repeat_next_delay = 2

    def __init__(self, attribute_name, low=None, high=None, step=None,
                 value=None, display_name=None):
        locked = low is None or high is None or step is None or value is None
        super().__init__(attribute_name, locked, display_name)
        self.low = low or 0
        self.high = high or self.low + 1
        self.step = step or 0.1
        self.value = value or 0.5
        self.current_direction = 0
        self.repeat_counter = 0
        self.sig_figs = min([p for p in range(-2, 9)
                             if abs(self.step - round(self.step, p)) < 1e-8])

    def update(self, key_events):
        if self.highlighted and not self.locked:
            self._handle_input(key_events)

    def _handle_input(self, key_events):
        if (pygame.KEYDOWN, pygame.K_PERIOD) in key_events:
            self.value = min(self.value + self.step, self.high)
            self.current_direction = 1
            self.repeat_counter = self.repeat_first_delay
        elif (pygame.KEYDOWN, pygame.K_COMMA) in key_events:
            self.value = max(self.value - self.step, self.low)
            self.current_direction = -1
            self.repeat_counter = self.repeat_first_delay
        elif ((pygame.KEYUP, pygame.K_PERIOD) in key_events
              or (pygame.KEYUP, pygame.K_COMMA) in key_events):
            self.current_direction = 0

        self.repeat_counter -= 1
        if self.current_direction and not self.repeat_counter:
            self.repeat_counter = self.repeat_next_delay
            if self.current_direction > 0:
                self.value = min(self.value + self.step, self.high)
            else:
                self.value = max(self.value - self.step, self.low)

    def draw(self, override_lock=False):
        super().draw(override_lock)
        if self.locked and not override_lock:
            return

        margin_px = self.local_rect.width * self.margin_horizontal
        line_y = 0.65 * self.local_rect.height
        value_x = ((self.value - self.low) / (self.high - self.low)
                   * (1 - 2 * self.margin_horizontal)
                   + self.margin_horizontal)
        pygame.draw.line(self.panel, self.line_color,
                         (margin_px, line_y), (self.local_rect.width - margin_px, line_y))
        triangle_points = [(value_x, 0.65), (value_x - 0.02, 0.61), (value_x + 0.02, 0.61)]
        triangle_points = [(point[0] * self.local_rect.width, point[1] * self.local_rect.height)
                           for point in triangle_points]
        pygame.draw.polygon(self.panel, (50, 50, 200), triangle_points)
        pygame.draw.aalines(self.panel, (255, 255, 255), True, triangle_points)
        text.render_text(self.panel, self.font, self.format_number(self.low),
                         (self.margin_horizontal, 0.75), size=0.6, justify=text.TOP)
        text.render_text(self.panel, self.font, self.format_number(self.high),
                         (1 - self.margin_horizontal, 0.75), size=0.6, justify=text.TOP)
        text.render_text(self.panel, self.font, self.format_number(self.value), (value_x, 0.50),
                         size=0.7, justify=text.BOTTOM)

    def format_number(self, number):
        if self.sig_figs <= 0:
            return str(int(round(number, self.sig_figs)))
        else:
            return "{:.02f}".format(number)


if __name__ == "__main__":
    from pygame.locals import *

    import config

    settings = config.DisplaySettings()
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(settings.screen_resolution, pygame.FULLSCREEN)
    pygame.display.set_caption('ZeroGee')
    clock = pygame.time.Clock()
    configurator = ShipConfigurator(screen, "Pegasus")

    def check_for_termination():
        pressed_keys = pygame.key.get_pressed()
        return pressed_keys[pygame.K_ESCAPE]

    while not check_for_termination():
        pygame.event.pump()

        configurator.update()
        configurator.draw()

        pygame.display.flip()
        clock.tick(1 / settings.tick_size)
