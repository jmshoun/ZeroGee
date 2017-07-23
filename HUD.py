#!/usr/bin/env python3

import pygame
import pygame.freetype

import text


class HUD(object):
    def __init__(self, panel):
        self.time = 0
        self.speed = 0
        self.panel = panel
        self.fuel_mass = None
        self.primary_font = pygame.freetype.Font('fonts/digital-7.ttf', 40)
    
    def update(self, time, status):
        self.time = time
        self.speed, self.fuel_mass = status
    
    def draw(self):
        time_text = "{0:>05.2f}".format(self.time)
        speed_text = "{0:>05.2f}".format(self.speed)
        fuel_text = "{0:>05.1f}".format(self.fuel_mass)

        text.render_text(self.panel, self.primary_font, "LEVEL 1", (0.05, 0.05), size=2)
        text.render_text(self.panel, self.primary_font, time_text, (0.05, 0.20), size=2)
        text.render_text(self.panel, self.primary_font, speed_text, (0.05, 0.35), size=2)
        text.render_text(self.panel, self.primary_font, fuel_text, (0.05, 0.50), size=2)
