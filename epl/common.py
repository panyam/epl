
class IEnv(object):
    """ An environment provides mappings between a variable and its values. """
    def __init__(self, parent = None):
        self.parent = parent

    def get(self, var):
        """ Applies a given function on a variable within this environment. """
        pass

    def push(self):
        """ Create a new environment by extending this one with new variable bindings. """
        return self.__class__(self)

    def extend(self, **var_and_values):
        """ Create a new environment by extending this one with new variable bindings. """
        return self.push().set(**var_and_values)

class DefaultEnv(IEnv):
    """ A default environment. """
    def __init__(self, parent = None, **values):
        IEnv.__init__(self, parent)
        self.values = values.copy()

    def get(self, var):
        """ Applies a given function on a variable within this environment. """
        if var in self.values: return self.values[var]
        elif self.parent: return self.parent.get(var)
        else:
            import ipdb ; ipdb.set_trace()
            return None

    def setone(self, key, value):
        self.values[key] = value
        return self

    def set(self, **var_and_values):
        for k,v in var_and_values.items():
            self.values[k] = v
        return self
