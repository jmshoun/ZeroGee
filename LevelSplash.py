#!/usr/bin/env python3

import pygame

import config


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
        self.time -= config.TICK_SIZE
        if self.time < 0:
            self.finished = True
        return self.finished
    
    def draw(self):
        self.screen.blit(self.text_surface, self.rect)
