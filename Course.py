#!/usr/bin/env python3

import yaml

import Gate
import FinishBox


class Course(object):
    def __init__(self, panel, course_path):
        with open(course_path) as course_file:
            course_dict = yaml.load(course_file.read())

        self.gates = [Gate.Gate.from_dict(panel, gate)
                      for gate in course_dict["gates"]]
        self.gates[0].status = Gate.STATUS_NEXT
        self.gate_sequence = course_dict["gate_sequence"]
        self.finish_box = FinishBox.FinishBox(panel, course_dict["finish_box"])

        self.current_gate_index = 0
        self.last_gate = 0
        self.num_gates = len(self.gate_sequence)
        self.current_gate = self.gate_sequence[self.current_gate_index]
    
    def update(self, ship_position):
        for gate in self.gates:
            updated_status = gate.update(ship_position)
            if updated_status:
                self._update_gate_status()
        
        self.finish_box.update(ship_position)

    def status(self):
        return self.current_gate_index, self.num_gates
    
    def _update_gate_status(self):
        self._update_last_gate()
        self._update_current_gate()
        
        self.current_gate_index += 1
        self.last_gate = self.current_gate
        
        self._update_next_gate()
    
    def _update_last_gate(self):
        if self.current_gate_index > 0:
            self.gates[self.last_gate].status = Gate.STATUS_OTHER
    
    def _update_current_gate(self): 
        self.gates[self.current_gate].status = Gate.STATUS_LAST
    
    def _update_next_gate(self):
        if self.current_gate_index < len(self.gate_sequence):
            self.current_gate = self.gate_sequence[self.current_gate_index]
            self.gates[self.current_gate].status = Gate.STATUS_NEXT
    
    def draw(self, camera_position):
        for gate in self.gates:
            gate.draw(camera_position)
        self.finish_box.draw(camera_position)
