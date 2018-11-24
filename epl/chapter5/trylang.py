
import typing
from epl.unions import *
from epl.chapter4 import lazylang
from epl.chapter5 import continuations

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

class Eval(continuations.Eval):
    __caseon__ = Expr

    @case("tryexpr")
    def valueOfTry(self, tryexpr, env, cont):
        return self(tryexpr, env, TryCont(tryexpr, env, cont))

    @case("raiseexpr")
    def valueOfRaise(self, raiseexpr, env, cont):
        return self(raiseexpr, env, RaiseCont(cont))

class TryCont(continuations.Cont):
    def __init__(self, Eval, env, cont, tryexpr):
        continuations.Cont(Eval, env, cont)
        self.tryexpr = tryexpr

    def start(self):
        return self.Eval(self.tryexpr.expr, self.env, self)

    def apply(self, result):
        # TODO - How about the raise case?
        return self.cont.apply(result)
