#!/usr/bin/env python3

import pygame

import Ship
import HUD
import Course
import LevelSplash

class Level:
    def __init__(self, screen):
        self.screen = screen
        self.start_time = pygame.time.get_ticks()
        self.camera_position = [0, 0]
        self.main_panel = screen.subsurface(pygame.Rect(0, 0, 1000, 768))
        self.hud_panel = screen.subsurface(pygame.Rect(1000, 0, 360, 768))
        
        self.ship = Ship.Ship(self.main_panel, (-0.1, 0), -90)
        self.hud = HUD.HUD(self.hud_panel)
        self.course = Course.Course(self.main_panel)
        self.level_splash = LevelSplash.LevelSplash(self.screen, "Go!", (255, 0, 255), 2.0)
    
    def update(self):
        self.current_time = (pygame.time.get_ticks() - self.start_time) / 1000
        
        self.ship.update()
        self.camera_position = self.ship.camera_position()
        
        self.hud.update(self.current_time - self.course.finish_box.timer, self.ship.status())
        self.course.update(self.ship.position())
        self.level_splash.update()
        
        return
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.hud.draw()
        self.course.draw(self.camera_position)
        self.ship.draw(self.camera_position)
        if not self.level_splash.finished:
            self.level_splash.draw()
        
        return