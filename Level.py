#!/usr/bin/env python3

import pygame

import Ship
import HUD
import Gate

class Level:
    def __init__(self, screen):
        self.screen = screen
        self.start_time = pygame.time.get_ticks()
        self.camera_position = [0, 0]
        
        self.ship = Ship.Ship(screen, (0, 0), 0)
        self.hud = HUD.HUD(screen)
        self.gates = [Gate.Gate(screen, (300, 300), 0, 'next')]
    
    def update(self):
        self.current_time = (pygame.time.get_ticks() - self.start_time) / 1000
        
        self.ship.update()
        self.camera_position = self.ship.camera_position()
        for gate in self.gates:
            gate.update(self.ship.position())
        self.hud.update(self.current_time, self.ship.status())
        
        return
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.hud.draw()
        for gate in self.gates:
            gate.draw(self.camera_position)
        self.ship.draw(self.camera_position)
        
        return