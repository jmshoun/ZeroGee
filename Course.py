#!/usr/bin/env python3

import yaml

import Gate
import FinishBox


class Course(object):
    def __init__(self, panel, course_path):
        with open(course_path) as course_file:
            course_dict = yaml.load(course_file.read())

        if "gates" in course_dict.keys():
            self.gates = [Gate.Gate.from_dict(panel, gate)
                          for gate in course_dict["gates"]]
            self.gates[0].status = Gate.Gate.STATUS_NEXT
            self.gate_sequence = course_dict["gate_sequence"]
        else:
            self.gates = []
            self.gate_sequence = []
        if "proxies" in course_dict.keys():
            self.proxies = [Gate.Proxy.from_dict(panel, proxy)
                            for proxy in course_dict["proxies"]]
        else:
            self.proxies = []
        self.finish_box = FinishBox.FinishBox(panel, course_dict["finish_box"])

        self.current_gate_index = 0
        self.last_gate = 0
        self.num_gates = len(self.gate_sequence)
        if self.num_gates:
            self.current_gate = self.gate_sequence[self.current_gate_index]

    @property
    def bounding_box(self):
        return (self._extremum(min, "x"), self._extremum(max, "x"),
                self._extremum(min, "y"), self._extremum(max, "y"))

    def _extremum(self, func, member):
        extreme = getattr(self.finish_box.position, member)
        if len(self.gates):
            extreme_gate = func([getattr(gate.position, member) for gate in self.gates])
            extreme = func(extreme, extreme_gate)
        if len(self.proxies):
            extreme_proxy = func([getattr(proxy.position, member) for proxy in self.proxies])
            extreme = func(extreme, extreme_proxy)
        return extreme
    
    def update(self, ship_position):
        for gate in self.gates:
            updated_status = gate.update(ship_position)
            if updated_status:
                self._update_gate_status()
        for proxy in self.proxies:
            proxy.update(ship_position)

        if self.current_gate_index == len(self.gates):
            self.finish_box.locked = False
        self.finish_box.update(ship_position)

    @property
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
            self.gates[self.last_gate].status = Gate.Gate.STATUS_OTHER
    
    def _update_current_gate(self): 
        self.gates[self.current_gate].status = Gate.Gate.STATUS_LAST
    
    def _update_next_gate(self):
        if self.current_gate_index < len(self.gate_sequence):
            self.current_gate = self.gate_sequence[self.current_gate_index]
            self.gates[self.current_gate].status = Gate.Gate.STATUS_NEXT
    
    def draw(self, camera_position):
        for gate in self.gates:
            gate.draw(camera_position)
        for proxy in self.proxies:
            proxy.draw(camera_position)
        self.finish_box.draw(camera_position)
