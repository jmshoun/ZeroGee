#!/usr/bin/env python3

import pygame

import Ship
import HUD
import Gate
import FinishBox

class Level:
    def __init__(self, screen):
        self.screen = screen
        self.start_time = pygame.time.get_ticks()
        self.camera_position = [0, 0]
        self.main_panel = screen.subsurface(pygame.Rect(0, 0, 1000, 768))
        self.hud_panel = screen.subsurface(pygame.Rect(1000, 0, 360, 768))
        
        self.ship = Ship.Ship(self.main_panel, (-0.1, 0), -90)
        self.hud = HUD.HUD(self.hud_panel)
        self.gates = [Gate.Gate(self.main_panel, (0, 0), 90, Gate.STATUS_NEXT),
                      Gate.Gate(self.main_panel, (50, 0), 90, Gate.STATUS_OTHER),
                      Gate.Gate(self.main_panel, (60, 10), 0, Gate.STATUS_OTHER),
                      Gate.Gate(self.main_panel, (60, 30), 0, Gate.STATUS_OTHER),
                      Gate.Gate(self.main_panel, (50, 40), 90, Gate.STATUS_OTHER),
                      Gate.Gate(self.main_panel, (0, 40), 90, Gate.STATUS_OTHER)]
        self.finish_box = FinishBox.FinishBox(self.main_panel, (-8, 40))
        
        self.gate_sequence = [0, 1, 2, 3, 4, 5]
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
                if self.current_gate_index > 0:
                    self.gates[self.last_gate].status = Gate.STATUS_OTHER
                    
                self.current_gate_index += 1
                self.gates[self.current_gate].status = Gate.STATUS_LAST
                self.last_gate = self.current_gate
                
                if self.current_gate_index < len(self.gate_sequence):
                    self.current_gate = self.gate_sequence[self.current_gate_index]
                    self.gates[self.gate_sequence[self.current_gate]].status = Gate.STATUS_NEXT
                    
        self.hud.update(self.current_time - self.finish_box.timer, self.ship.status())
        self.finish_box.update(self.ship.position())
        
        return
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.hud.draw()
        for gate in self.gates:
            gate.draw(self.camera_position)
        self.finish_box.draw(self.camera_position)
        self.ship.draw(self.camera_position)
        
        return