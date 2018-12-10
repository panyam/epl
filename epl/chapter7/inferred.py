
import typing
from epl import bp
from taggedunion import *
from epl.chapter7 import typed
from epl.chapter5 import trylang
from epl.chapter7.utils import *

class TypeVar(object):
    serial_counter = 0
    def __init__(self):
        self.serial = self.__cls__.serial_counter
        self.__cls__.serial_counter += 1

    def __repr__(self):
        return "TVar(%d)".format(self.serial)

    def __eq__(self, another):
        self.serial == another.serial

    def __hash__(self):
        return self.serial

class Type(typed.Type):
    typevar = Variant(TypeVar)

class Substitutions(object):
    def __init__(self):
        self.bindings = {}

    def extend(self, tvar, tvalue):
        """ Substitutes tvar with tvalue in all bindings and then adds a new binding ( tvar -> tvalue ). """
        assert tvar not in self.bindings
        self.substitute(tvar, tvalue)
        self.bindings[tvar] = tvalue

class Substitute(CaseMatcher):
    __caseon__ = Type

    @case("leaf")
    def substituteLeaf(self, leaf, substitutions):
        return leaf

    @case("tup")
    def substituteTup(self, tup, substitutions):
        childtypes = [self(t, substitutions) for t in tup.children]
        return Type.as_tup(childtypes)

    @case("func")
    def substituteFunc(self, func, substitutions):
        argtypes = [self(t, substitutions) for t in func.argtypes]
        rettype = [self(t, substitutions) for t in func.rettype]
        return Type.as_func(argtypes, rettype)

    @case("tagged")
    def substituteTagged(self, tagged, substitutions):
        thetype = self(tagged.thetype, substitutions)
        return Type.as_tagged(tagged.name, thetype)

    @case("typevar")
    def substituteTypeVar(self, typevar, substitutions):
        return substitutions.get(typevar, typevar)

if False:
    class Unify(CaseMatcher):
        """ Our type unifier. """
        __caseon__ = trylang.Expr

