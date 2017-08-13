import yaml
import pygame
from pygame.math import Vector2

import waypoint
import hazard
import finishbox


class Course(object):
    def __init__(self, panel, dict_):
        gate_spec = dict_.get("gates", []), dict_.get("gate_sequence", [])
        proxy_spec = dict_.get("proxies", [])
        gravity_zone_spec = dict_.get("gravity_zones", [])

        self.gate_set = GateSet(panel, *gate_spec)
        self.proxy_set = ProxySet(panel, proxy_spec)
        self.gravity_zone_set = GravityZoneSet(panel, gravity_zone_spec)
        self.finish_box = finishbox.FinishBox(panel, dict_["finish_box"])

    @classmethod
    def from_file(cls, course_path):
        with open(course_path) as course_file:
            course_dict = yaml.load(course_file.read())
        return cls(course_dict)

    @property
    def bounding_rect(self):
        min_x, max_x, min_y, max_y = (self._extremum(min, "x"), self._extremum(max, "x"),
                                      self._extremum(min, "y"), self._extremum(max, "y"))
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def _extremum(self, func, member):
        extreme = getattr(self.finish_box.position, member)
        if self.gates:
            extreme_gate = func([getattr(gate.position, member) for gate in self.gates])
            extreme = func(extreme, extreme_gate)
        if self.proxies:
            extreme_proxy = func([getattr(proxy.position, member) for proxy in self.proxies])
            extreme = func(extreme, extreme_proxy)
        return extreme
    
    def update(self, ship_position):
        self.gate_set.update(ship_position)
        self.proxy_set.update(ship_position)

        if self.gate_set.is_complete and self.proxy_set.is_complete:
            self.finish_box.locked = False
        self.finish_box.update(ship_position)

    @property
    def status(self):
        return {"current_gate": self.gate_set.current_gate_index,
                "num_gates": self.gate_set.num_gates,
                "current_proxy": self.proxy_set.proxies_completed,
                "num_proxies": self.proxy_set.num_proxies}
    
    def draw(self, camera_position):
        self.gate_set.draw(camera_position)
        self.proxy_set.draw(camera_position)
        self.gravity_zone_set.draw(camera_position)
        self.finish_box.draw(camera_position)

    @property
    def gates(self):
        return self.gate_set.gates

    @property
    def proxies(self):
        return self.proxy_set.proxies

    @property
    def gravity_zones(self):
        return self.gravity_zone_set.zones

    def acceleration(self, ship_position):
        return self.gravity_zone_set.acceleration(ship_position)


class ProxySet(object):
    def __init__(self, panel, proxies):
        self.proxies = [waypoint.Proxy.from_dict(panel, proxy) for proxy in proxies]
        self.num_proxies = len(self.proxies)
        self.proxies_completed = 0

    def update(self, ship_position):
        for proxy in self.proxies:
            if proxy.update(ship_position):
                self.proxies_completed += 1

    def draw(self, camera_position):
        for proxy in self.proxies:
            proxy.draw(camera_position)

    @property
    def is_complete(self):
        return self.proxies_completed == self.num_proxies


class GateSet(object):
    def __init__(self, panel, gates, gate_sequence):
        self.gates = [waypoint.Gate.from_dict(panel, gate) for gate in gates]
        self.gate_sequence = gate_sequence
        self.num_gates = len(self.gate_sequence)
        self.current_gate_index = 0
        if self.gates:
            self.current_gate = self.gate_sequence[self.current_gate_index]
            self.last_gate = self.current_gate
            self.gates[self.current_gate].status = waypoint.Gate.STATUS_NEXT

    def update(self, ship_position):
        if not self.gates:
            return
        updated_status = self.gates[self.current_gate].update(ship_position)
        if updated_status:
            self._update_last_gate()
            self._update_current_gate()
            self._update_next_gate()

    def _update_last_gate(self):
        if self.current_gate_index > 0:
            self.gates[self.last_gate].status = waypoint.Gate.STATUS_OTHER
        self.last_gate = self.current_gate
        self.gates[self.last_gate].status = waypoint.Gate.STATUS_LAST

    def _update_current_gate(self):
        self.current_gate_index += 1
        if self.current_gate_index < self.num_gates:
            self.current_gate = self.gate_sequence[self.current_gate_index]

    def _update_next_gate(self):
        if not self.is_complete:
            self.gates[self.current_gate].status = waypoint.Gate.STATUS_NEXT

    def draw(self, camera_position):
        for gate in self.gates:
            gate.draw(camera_position)

    @property
    def is_complete(self):
        return self.current_gate_index == len(self.gate_sequence)


class GravityZoneSet(object):
    def __init__(self, panel, gravity_zones):
        self.zones = [hazard.GravityZone.from_dict(panel, zone) for zone in gravity_zones]

    def draw(self, camera_position):
        for zone in self.zones:
            zone.draw(camera_position)

    def acceleration(self, ship_position):
        acceleration = Vector2()
        for zone in self.zones:
            acceleration += zone.current_acceleration(ship_position)
        return acceleration
