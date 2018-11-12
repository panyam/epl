
from ipdb import set_trace

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

class Variant(object):
    def __init__(self, vartype, checker_name = None):
        self.vartype = vartype
        self.checker_name = checker_name

class UnionMeta(type):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        def makechecker(vtype):
            return property(lambda x: isinstance(x.value, vtype))

        def makegetter(checker, vtype):
            def getter(self):
                if getattr(self, checker):
                    return self._variant_value
                else:
                    assert False, "Invalid variant type getter called"
            return property(getter)

        def makeconstructor(vtype):
            def constructor(cls, *args, **kwargs):
                value = vtype(*args, **kwargs)
                out = cls()
                out._variant_value = value
                return out
            return classmethod(constructor)

        __variants__ = getattr(x, "__variants__", [])[:]
        newfields = {}
        for vname,variant in x.__dict__.items():
            if not isinstance(variant, Variant): continue

            __variants__.append((vname, variant))
            if not variant.checker_name:
                variant.checker_name = "is_" + vname

            vtype,checker = variant.vartype, variant.checker_name 
            newfields[checker] = makechecker(vtype)
            newfields[vname] = makegetter(checker, vtype)
            newfields["as_" + vname] = makeconstructor(vtype)
        for k,v in newfields.items(): setattr(x,k,v)
        setattr(x, "__variants__", __variants__)
        return x

class Union(metaclass = UnionMeta):
    @property
    def value(self):
        return self._variant_value

    @classmethod
    def hasvariant(cls, name):
        return name in (n for n,v in cls.__variants__)

def case(name):
    def decorator(func):
        func.__case_matching_on__ = name
        return func
    return decorator

class CaseMatcherMeta(type):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        caseon = getattr(x, "__caseon__", None)
        assert caseon or name == "CaseMatcher", "Case matcher MUST have a __caseon__ class attribute to indicate union type we can switch on"
        x.__cases__ = getattr(x, "__cases__", {}).copy()
        for name,casefunc in x.__dict__.items():
            matched_on = getattr(casefunc, "__case_matching_on__", None)
            if not matched_on: continue

            if not caseon.hasvariant(matched_on):
                assert False, "Selected union (%s) type does not have variant being matched on (%s)." % (caseon, matched_on)
            x.__cases__[matched_on] = casefunc
        return x

class CaseMatcher(metaclass = CaseMatcherMeta):
    def select(self, expr : Union):
        for vname, variant in expr.__variants__:
            if getattr(expr, variant.checker_name):
                return self._cases[vname], expr.variant_value
        assert False, "Case not matched"
