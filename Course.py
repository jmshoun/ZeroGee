import yaml

import waypoint
import FinishBox


class Course(object):
    def __init__(self, panel, course_path):
        with open(course_path) as course_file:
            course_dict = yaml.load(course_file.read())

        gate_spec = course_dict.get("gates", []), course_dict.get("gate_sequence", [])
        self.gate_set = GateSet(panel, *gate_spec)
        proxy_spec = course_dict.get("proxies", [])
        self.proxy_set = ProxySet(panel, proxy_spec)
        self.finish_box = FinishBox.FinishBox(panel, course_dict["finish_box"])

    @property
    def bounding_box(self):
        return (self._extremum(min, "x"), self._extremum(max, "x"),
                self._extremum(min, "y"), self._extremum(max, "y"))

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
        return self.gate_set.current_gate_index, self.gate_set.num_gates
    
    def draw(self, camera_position):
        self.gate_set.draw(camera_position)
        self.proxy_set.draw(camera_position)
        self.finish_box.draw(camera_position)

    @property
    def gates(self):
        return self.gate_set.gates

    @property
    def proxies(self):
        return self.proxy_set.proxies


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
