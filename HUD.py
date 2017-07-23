#!/usr/bin/env python3

import pygame
import pygame.freetype

import text


class HUD(object):
    def __init__(self, panel):
        self.time = 0
        self.gate_number = 0
        self.total_gates = 0
        self.speed = 0
        self.panel = panel
        self.fuel_mass = None
        self.primary_font = pygame.freetype.Font('fonts/digital-7 (mono italic).ttf')
    
    def update(self, time, course_status, ship_status):
        self.time = time
        self.gate_number, self.total_gates = course_status
        self.speed, self.fuel_mass = ship_status
        self.fuel_mass = max(self.fuel_mass, 0)
    
    def draw(self):
        gate_text = "{0:02d} / {1:02d}".format(self.gate_number, self.total_gates)
        time_text = "{0:>05.2f}".format(self.time)
        speed_text = "{0:>05.2f}".format(self.speed)
        fuel_text = "{0:>05.1f}".format(self.fuel_mass)

        text.render_text(self.panel, self.primary_font, "GATE NUMBER:", (0.05, 0.05),
                         foreground=text.BLUE, size=1.2)
        text.render_text(self.panel, self.primary_font, gate_text, (0.05, 0.10), size=2)
        text.render_text(self.panel, self.primary_font, "TIME:", (0.05, 0.20),
                         foreground=text.BLUE, size=1.2)
        text.render_text(self.panel, self.primary_font, time_text, (0.05, 0.25), size=2)
        text.render_text(self.panel, self.primary_font, "SPEED:", (0.05, 0.35),
                         foreground=text.BLUE, size=1.2)
        text.render_text(self.panel, self.primary_font, speed_text, (0.05, 0.40), size=2)
        text.render_text(self.panel, self.primary_font, "FUEL LEFT:", (0.05, 0.50),
                         foreground=text.BLUE, size=1.2)
        text.render_text(self.panel, self.primary_font, fuel_text, (0.05, 0.55), size=2)
