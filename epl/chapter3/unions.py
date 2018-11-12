from ipdb import set_trace

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

    @classmethod
    def numvariants(cls):
        return len(cls.__variants__)

def case(name):
    def decorator(func):
        func.__case_matching_on__ = name
        return func
    return decorator

class CaseMatcherMeta(type):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        caseon = getattr(x, "__caseon__", None)
        if not caseon and name != "CaseMatcher":
            raise Exception("Case matcher MUST have a __caseon__ class attribute to indicate union type we can switch on")

        x.__cases__ = getattr(x, "__cases__", {}).copy()
        for name,casefunc in x.__dict__.items():
            if not hasattr(casefunc, "__case_matching_on__"): continue

            matched_on = casefunc.__case_matching_on__
            # TODO - Should we treat matched_on == None as the "default" case?

            if not caseon.hasvariant(matched_on):
                raise Exception("Selected union (%s) type does not have variant being matched on (%s)." % (caseon, matched_on))
            x.__cases__[matched_on] = casefunc
        if x.__cases__ and len(x.__cases__) != caseon.numvariants():
            raise Exception("Not all variants in union (%s) have been matched" % caseon)
        return x

class CaseMatcher(metaclass = CaseMatcherMeta):
    def select(self, expr : Union):
        for vname, variant in expr.__variants__:
            if getattr(expr, variant.checker_name):
                return self._cases[vname], expr.variant_value
        assert False, "Case not matched"
