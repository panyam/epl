
import typing
from epl.unions import *
from epl.chapter4 import lazylang

class TryCatch(object):
    """ A try catch expression. """
    def __init__(self, expr, varname, excexpr):
        self.expr = expr
        self.varname = varname
        self.exception = exception

    def printables(self):
        yield 0, "Try:"
        yield 1, self.expr.printables()
        yield 1, "Catch (%s)" % self.varname
        yield 2, self.exception.printables()

    def __eq__(self, another):
        return self.expr == another.expr and        \
                self.varname == another.varname and \
                self.exception == another.exception

class Raise(object):
    def __init__(self, expr):
        self.expr = expr

    def printables(self):
        yield 0, "Raise:"
        yield 1, self.expr.printables()

    def __eq__(self, another):
        return self.expr == another.expr

class Expr(lazylang.Expr):
    tryexpr = Variant(TryCatch)
    raiseexpr = Variant(Raise)

class Eval(lazylang.Eval):
    __caseon__ = Expr

    @case("tryexpr")
    def valueOfTry(self, tryexpr, env):
        pass

    @case("raiseexpr")
    def valueOfRaise(self, raiseexpr, env):
        pass
