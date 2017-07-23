#!/usr/bin/env python3

import random

import pygame

import Ship
import HUD
import Course
import Starfield
import config

settings = config.DisplaySettings()
STATUS_READY = 0
STATUS_SET = 1
STATUS_GO = 2
STATUS_FINISHED = 3
STATUS_FALSE_START = 4

PANEL_SIZES = {
    (1360, 768): {
        "main_rect": [0, 0, 1000, 768],
        "hud_rect": [1000, 0, 360, 768]
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
    def __init__(self, screen, course_path):
        self.screen = screen
        self.start_time = pygame.time.get_ticks()
        self.current_time = 0
        self.status = STATUS_READY
        
        self.main_panel = Panel(screen.subsurface(pygame.Rect(*panel_sizes["main_rect"])))
        self.hud_panel = Panel(screen.subsurface(pygame.Rect(*panel_sizes["hud_rect"])))
        
        self.ship = Ship.Ship(self.main_panel.surface, (-0.1, 0), -90)
        self.hud = HUD.HUD(self.hud_panel.surface)
        self.course = Course.Course(self.main_panel.surface, course_path)
        self.starfield = Starfield.Starfield(self.main_panel.surface)
        self.level_splash = LevelSplash(self.screen, "Ready", (255, 0, 255), 10000)
        
        self.camera_position = self.ship.camera_position()
    
    def update(self):
        self.level_splash.update()
        if self.status is STATUS_READY:
            self._update_ready()
        elif self.status is STATUS_SET:
            self._update_set()
        elif self.status is STATUS_GO:
            self._update_go()
        self.hud.update(self.current_time, self.course.status(), self.ship.status())
    
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
    
    def _update_go(self):
        if self.course.finish_box.timer == 0:
            self.current_time = (pygame.time.get_ticks() - self.start_time) / 1000
        
        self.ship.update()
        self.camera_position = self.ship.camera_position()
        
        self.course.update(self.ship.position())
        if self.course.finish_box.finished:
            self.status = STATUS_FINISHED
            self.level_splash = LevelSplash(self.screen, "Finished", (255,  0, 255), 5)
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.main_panel.draw()
        self.hud_panel.draw()
        self.hud.draw()
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
