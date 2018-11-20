
import typing
from epl.unions import *
from epl.chapter3 import letreclang

class NewRefExpr(object):
    """ Creates a new reference. """
    def __init__(self, expr):
        self.expr = expr

    def printables(self):
        yield 0, "NewRef:"
        yield 1, self.expr.printables()

    def __eq__(self, another):
        return self.expr == another.expr

class DeRefExpr(object):
    def __init__(self, expr):
        self.expr = expr

    def printables(self):
        yield 0, "DeRef:"
        yield 1, self.expr.printables()

    def __eq__(self, another):
        return self.expr == another.expr

class SetRefExpr(object):
    def __init__(self, ref, value):
        self.ref = ref
        self.value = value

    def printables(self):
        yield 0, "SetRef:"
        yield 1, "Ref:"
        yield 2, self.ref.printables()
        yield 1, "Value:"
        yield 2, self.value.printables()

    def __eq__(self, another):
        return self.ref == another.ref and \
               self.value == another.value

class BlockExpr(object):
    def __init__(self, exprs):
        self.exprs = exprs

    def printables(self):
        yield 0, "Begin:"
        for expr in self.exprs:
            yield 1, expr.printables()
        yield 0, "End"

    def __eq__(self, another):
        return self.exprs == another.exprs

class Expr(letreclang.Expr):
    newref = Variant(NewRefExpr)
    deref = Variant(DeRefExpr)
    setref = Variant(SetRefExpr)
    block = Variant(BlockExpr)

class Eval(letreclang.Eval):
    __caseon__ = Expr

    @case("newref")
    def valueOfNewRef(self, newref, env):
        assert False

    @case("deref")
    def valueOfDeRef(self, deref, env):
        assert False

    @case("setref")
    def valueOfSetRef(self, setref, env):
        assert False

    @case("block")
    def valueOfBlock(self, block, env):
        assert False
