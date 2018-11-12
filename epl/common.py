
from ipdb import set_trace
from unions import *

class IEnv(object):
    """ An environment provides mappings between a variable and its values. """
    def __init__(self, parent = None):
        self.parent = parent

    def get(self, var):
        """ Applies a given function on a variable within this environment. """
        pass

    def extend(self, **var_and_values):
        """ Create a new environment by extending this one with new variable bindings. """
        return self

class DefaultEnv(IEnv):
    """ A default environment. """
    def __init__(self, parent = None):
        IEnv.__init__(self, parent)
        self.values = {}

    def get(self, var):
        """ Applies a given function on a variable within this environment. """
        return self.values[var]

    def set(self, **var_and_values):
        for k,v in var_and_values.items():
            self.values[k] = v
        return self

    def extend(self, **var_and_values):
        """ Extend the environment with new variable bindings. """
        out = DefaultEnv(self)
        return out.set(**var_and_values)

