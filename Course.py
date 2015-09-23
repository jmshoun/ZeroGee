#!/usr/bin/env python3

import pygame

import Gate
import FinishBox

class Course:
    def __init__(self, panel):
        self.gates = [Gate.Gate(panel, (0, 0), 90, Gate.STATUS_NEXT),
                      Gate.Gate(panel, (50, 0), 90, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (72.51, 9.32), 45, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (81.83, 31.83), 0, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (72.51, 54.34), -45, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (50, 63.66), 90, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (0, 63.66), 90, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (-50, 63.66), 90, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (-72.51, 54.34), 45, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (-81.83, 31.83), 0, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (-72.51, 9.32), -45, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (-50, 0), 90, Gate.STATUS_OTHER),
                      Gate.Gate(panel, (-20, 0), 90, Gate.STATUS_OTHER)]
        self.finish_box = FinishBox.FinishBox(panel, (-12, 0))
        
        self.gate_sequence = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.current_gate_index = 0
        self.last_gate = 0
        self.current_gate = self.gate_sequence[self.current_gate_index]
    
    def update(self, ship_position):
        for gate in self.gates:
            updated_status = gate.update(ship_position)
            if updated_status:
                self._update_gate_status()
        
        self.finish_box.update(ship_position)
        return
    
    def _update_gate_status(self):
        self._update_last_gate()
        self._update_current_gate()
        
        self.current_gate_index += 1
        self.last_gate = self.current_gate
        
        self._update_next_gate()
        return
    
    def _update_last_gate(self):
        if self.current_gate_index > 0:
            self.gates[self.last_gate].status = Gate.STATUS_OTHER
        return
    
    def _update_current_gate(self): 
        self.gates[self.current_gate].status = Gate.STATUS_LAST
        return
    
    def _update_next_gate(self):
        if self.current_gate_index < len(self.gate_sequence):
            self.current_gate = self.gate_sequence[self.current_gate_index]
            self.gates[self.current_gate].status = Gate.STATUS_NEXT
        return
    
    def draw(self, camera_position):
        for gate in self.gates:
            gate.draw(camera_position)
        self.finish_box.draw(camera_position)
        return