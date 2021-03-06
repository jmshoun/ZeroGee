import random

import pygame

import hud
import starfield
import minimap
import config
import course
import ship
import waypoint

settings = config.DisplaySettings()
STATUS_READY = 0
STATUS_SET = 1
STATUS_GO = 2
STATUS_FINISHED = 3
STATUS_FALSE_START = 4

PANEL_SIZES = {
    (1360, 768): {
        "main_rect": [0, 0, 1000, 768],
        "hud_rect": [1000, 0, 360, 500],
        "minimap_rect": [1000, 500, 360, 268]
    },
    (1920, 1080): {
        "main_rect": [0, 0, 1440, 1080],
        "hud_rect": [1440, 0, 480, 720],
        "minimap_rect": [1440, 720, 480, 360]
    }
}

panel_sizes = PANEL_SIZES[settings.screen_resolution]


class Panel(object):
    def __init__(self, surface, border_width=1, border_color=(200, 200, 200)):
        self.surface = surface
        self.border_width = border_width
        self.border_color = border_color

    def draw(self):
        pygame.draw.rect(self.surface, self.border_color,
                         self.surface.get_rect(), self.border_width)


class Level(object):
    def __init__(self, screen, course_dict, ship_dict, comparison_splits=None):
        self.screen = screen
        self.start_time = pygame.time.get_ticks()
        self.current_time = 0
        self.status = STATUS_READY
        
        self.main_panel = Panel(screen.subsurface(pygame.Rect(*panel_sizes["main_rect"])))
        self.hud_panel = Panel(screen.subsurface(pygame.Rect(*panel_sizes["hud_rect"])))
        self.minimap_panel = Panel(screen.subsurface(pygame.Rect(*panel_sizes["minimap_rect"])))
        
        self.ship = ship.ship_from_dict(ship_dict, self.main_panel.surface)
        self.ship.set_position((-0.1, 0), 0)
        self.course = course.Course(self.main_panel.surface, course_dict)
        self.active_splits = waypoint.Splits(self.course.num_waypoints)
        self.comparison_splits = comparison_splits if comparison_splits else self.active_splits

        self.starfield = starfield.Starfield(self.main_panel.surface)
        self.level_splash = LevelSplash(self.screen, "Ready", (255, 0, 255), 10000)

        self.hud = hud.HUD(self.hud_panel.surface)
        self.minimap = minimap.MiniMap(self.minimap_panel.surface, self.course, self.ship)
        self.camera_position = self.ship.camera_position
    
    def update(self):
        self.level_splash.update()
        if self.status is STATUS_READY:
            self._update_ready()
        elif self.status is STATUS_SET:
            self._update_set()
        elif self.status is STATUS_GO:
            self._update_go()
        self.hud.update(self.timing_status, self.course.status, self.ship.status)
    
    def _update_ready(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_SPACE]:
            self.status = STATUS_SET
            self.level_splash = LevelSplash(self.screen, "Set...", (255, 0, 255),
                                            .8 + random.random())
    
    def _update_set(self):
        pressed_keys = pygame.key.get_pressed()
        if self.level_splash.finished:
            self.status = STATUS_GO
            self.start_time = pygame.time.get_ticks()
            self.level_splash = LevelSplash(self.screen, "Go!", (255, 0, 255), 1.5)
        elif pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_LEFT] or \
                pressed_keys[pygame.K_RIGHT]:
            self.status = STATUS_FALSE_START
            self.level_splash = LevelSplash(self.screen, "False Start!",
                                            (255, 0, 255), 5)
            self.active_splits.status = "Disqualified"
    
    def _update_go(self):
        if self.course.finish_box.timer == 0:
            self.current_time = (pygame.time.get_ticks() - self.start_time) / 1000

        external_acceleration = self.course.acceleration(self.ship.position)
        self.ship.update(external_acceleration)
        self.camera_position = self.ship.camera_position
        self.course.update(self.ship.position)
        self.active_splits.update(self.current_time, self.course.waypoints_completed)

        if self.course.finish_box.finished:
            self.status = STATUS_FINISHED
            self.level_splash = LevelSplash(self.screen, "Finished", (255,  0, 255), 5)
            self.active_splits.set_final_time(self.current_time)

    @property
    def timing_status(self):
        current_waypoint = self.course.waypoints_completed - 1
        last_split = self.active_splits.split_times[current_waypoint]
        comparison_split = self.comparison_splits.split_times[current_waypoint]
        split_delta = last_split - comparison_split
        return {"current_time": self.current_time,
                "last_split": last_split,
                "split_delta": split_delta}
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.main_panel.draw()
        self.hud_panel.draw()
        self.minimap_panel.draw()
        self.hud.draw()
        self.minimap.draw()
        self.course.draw(self.camera_position)
        self.ship.draw(self.camera_position)
        self.starfield.draw(self.camera_position)
        if not self.level_splash.finished:
            self.level_splash.draw()


class LevelSplash(object):
    def __init__(self, screen, text, color, time):
        self.screen = screen
        self.text = text
        self.color = color
        self.time = time
        self.finished = False

        self.font = pygame.font.Font('fonts/Disco Nectar.ttf', 250)
        self.text_surface = self.font.render(self.text, True, color)
        self.rect = self.text_surface.get_rect()
        self.rect.center = self.screen.get_rect().center

    def update(self):
        self.time -= settings.tick_size
        if self.time < 0:
            self.finished = True
        return self.finished

    def draw(self):
        self.screen.blit(self.text_surface, self.rect)
