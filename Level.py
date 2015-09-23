#!/usr/bin/env python3

import random

import pygame

import Ship
import HUD
import Course
import LevelSplash

STATUS_READY = 0
STATUS_SET = 1
STATUS_GO = 2
STATUS_FINISHED = 3

class Level:
    def __init__(self, screen):
        self.screen = screen
        self.start_time = pygame.time.get_ticks()
        self.current_time = 0
        self.status = STATUS_READY
        
        self.main_panel = screen.subsurface(pygame.Rect(0, 0, 1000, 768))
        self.hud_panel = screen.subsurface(pygame.Rect(1000, 0, 360, 768))
        
        self.ship = Ship.Ship(self.main_panel, (-0.1, 0), -90)
        self.hud = HUD.HUD(self.hud_panel)
        self.course = Course.Course(self.main_panel)
        self.level_splash = LevelSplash.LevelSplash(self.screen, "Ready", (255, 0, 255), 0.7)
        
        self.camera_position = self.ship.camera_position()
    
    def update(self):
        self.level_splash.update()
        self.hud.update(self.current_time, self.ship.status())
        
        if self.status is STATUS_READY:
            self._update_ready()
        elif self.status is STATUS_SET:
            self._update_set()
        elif self.status is STATUS_GO:
            self._update_go()
        
        return
    
    def _update_ready(self):
        if self.level_splash.finished:
            self.status = STATUS_SET
            self.level_splash = LevelSplash.LevelSplash(self.screen, "Set...", (255, 0, 255),
                                                        .8 + random.random())
        return
    
    def _update_set(self):
        if self.level_splash.finished:
            self.status = STATUS_GO
            self.start_time = pygame.time.get_ticks()
            self.level_splash = LevelSplash.LevelSplash(self.screen, "Go!", (255, 0, 255), 1.5)
        
        return
    
    def _update_go(self):
        if self.course.finish_box.timer == 0:
            self.current_time = (pygame.time.get_ticks() - self.start_time) / 1000
        
        self.ship.update()
        self.camera_position = self.ship.camera_position()
        
        self.course.update(self.ship.position())
        if self.course.finish_box.finished:
            self.status = STATUS_FINISHED
            self.level_splash = LevelSplash.LevelSplash(self.screen, "Finished", (255,  0, 255), 5)
        
        return
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.hud.draw()
        self.course.draw(self.camera_position)
        self.ship.draw(self.camera_position)
        if not self.level_splash.finished:
            self.level_splash.draw()
        
        return