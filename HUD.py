#!/usr/bin/env python3

import math

import pygame

class HUD:
    def __init__(self, screen):
        self.time = 0
        self.speed = 0
        self.panel = screen.subsurface(pygame.Rect(1000, 0, 360, 768))
        self.primary_font = pygame.font.Font('fonts/Crysta.ttf', 40)
    
    def update(self, time, status):
        self.time = time
        self.speed, self.fuel_mass = status
        
        return
    
    def draw(self):
        title_surface = self.primary_font.render("LEVEL 1", True, (255, 255, 255))
        
        time_text = "{0:>05.2f}".format(self.time)
        time_surface = self.primary_font.render(time_text, True, (255, 255, 255))
        
        speed_text = "{0:>05.2f}".format(self.speed)
        speed_surface = self.primary_font.render(speed_text, True, (255, 255, 255))
        
        fuel_text = "{0:>05.1f}".format(self.fuel_mass)
        fuel_surface = self.primary_font.render(fuel_text, True, (255, 255, 255))
        
        self.panel.blit(title_surface, (10, 10))
        self.panel.blit(time_surface, (10, 100))
        self.panel.blit(speed_surface, (10, 190))
        self.panel.blit(fuel_surface, (10, 280))
        
        return