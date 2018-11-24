
class Lit(object):
    def __init__(self, value):
        while type(value) is Lit:
            value = value.value
        assert type(value) in (str, int, float, bool)
        self.value = value

    def __add__(self, another):
        return Lit(self.value + another.value)

    def __sub__(self, another):
        return Lit(self.value - another.value)

    def __eq__(self, another):
        if type(another) == type(self.value): return self.value == another
        elif type(self) != type(another): return False
        return self.value == another.value

    def __repr__(self):
        return "Val(%s:%s)" % (type(self.value), self.value)

    def printables(self):
        yield 0, "Val(%s:%s)" % (type(self.value), self.value)
