import pickle
import json
import hashlib

import waypoint


class Profile(object):
    def __init__(self, name, run_records=None):
        self.name = name
        self.run_records = run_records if run_records else {}

    @classmethod
    def from_dict(cls, dict_):
        run_records = {k: [RunRecord.from_dict(e) for e in v]
                       for k, v in dict_["run_records"].items()}
        return cls(dict_["name"], run_records)

    @classmethod
    def load(cls, name):
        try:
            with open(cls.filename_from_name(name), "rb") as file:
                dict_ = pickle.load(file)
            return cls.from_dict(dict_)
        except FileNotFoundError:
            return cls(name)

    def as_dict(self):
        return {"name": self.name,
                "run_records": {k: [e.as_dict() for e in v]
                                for k, v in self.run_records.items()}}

    def save(self):
        with open(self.filename_from_name(self.name), "wb") as file:
            pickle.dump(self.as_dict(), file)

    def add_record(self, course_dict, ship_dict, splits):
        course_hash = self.dict_hash(course_dict)
        if course_hash not in self.run_records:
            self.run_records[course_hash] = []
        self.run_records[course_hash] += [RunRecord(ship_dict, splits)]

    def fastest_run_splits(self, course_dict):
        course_hash = self.dict_hash(course_dict)
        if course_hash not in self.run_records.keys():
            return None
        sorted_records = sorted(self.run_records[course_hash], key=lambda record: record.run_time)
        return sorted_records[0].splits

    @staticmethod
    def filename_from_name(name):
        return "profiles/{}.p".format(name)

    @staticmethod
    def dict_hash(dict_):
        dict_string = json.dumps(dict_, sort_keys=True).encode("utf-8")
        hash_obj = hashlib.sha256(dict_string)
        return hash_obj.digest()


class RunRecord(object):
    def __init__(self, ship_dict, splits):
        self.ship_dict = ship_dict
        self.splits = splits

    @classmethod
    def from_dict(cls, dict_):
        splits = waypoint.Splits.from_dict(dict_["splits"])
        return cls(dict_["ship_dict"], splits)

    def as_dict(self):
        return {"ship_dict": self.ship_dict,
                "splits": self.splits.as_dict()}

    @property
    def run_time(self):
        return self.splits.final_time
