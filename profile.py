import pickle


class Profile(object):
    def __init__(self, name, course_bests=None):
        self.name = name
        self.course_bests = course_bests if course_bests else {}

    @classmethod
    def from_dict(cls, dict_):
        return cls(dict_["name"], dict_["course_bests"])

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
                "course_bests": self.course_bests}

    def save(self):
        with open(self.filename_from_name(self.name), "wb") as file:
            pickle.dump(self.as_dict(), file)

    @staticmethod
    def filename_from_name(name):
        return "profiles/{}.p".format(name)
