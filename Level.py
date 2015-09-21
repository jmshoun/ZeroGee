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
        
        self.ship = Ship.Ship(screen, (-0.1, 0), -90)
        self.hud = HUD.HUD(screen)
        self.gates = [Gate.Gate(screen, (0, 0), 90, Gate.STATUS_NEXT),
                      Gate.Gate(screen, (25, 0), 90, Gate.STATUS_OTHER)]
        
        self.gate_sequence = [0, 1, 1, 0]
        self.current_gate_index = 0
        self.last_gate = 0
        self.current_gate = self.gate_sequence[self.current_gate_index]
    
    def update(self):
        self.current_time = (pygame.time.get_ticks() - self.start_time) / 1000
        
        self.ship.update()
        self.camera_position = self.ship.camera_position()
        for gate in self.gates:
            updated_status = gate.update(self.ship.position())
            if updated_status:
                if self.current_gate > 0:
                    self.gates[self.last_gate].status = Gate.STATUS_OTHER
                    
                self.current_gate_index += 1
                self.gates[self.current_gate].status = Gate.STATUS_LAST
                self.last_gate = self.current_gate
                
                if self.current_gate_index < len(self.gate_sequence):
                    self.current_gate = self.gate_sequence[self.current_gate_index]
                    self.gates[self.gate_sequence[self.current_gate]].status = Gate.STATUS_NEXT
                    
        self.hud.update(self.current_time, self.ship.status())
        
        return
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.hud.draw()
        for gate in self.gates:
            gate.draw(self.camera_position)
        self.ship.draw(self.camera_position)
        
        return