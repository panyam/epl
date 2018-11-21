
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

    def valueOf(self, expr, env):
        return self(expr, env)

    @case("newref")
    def valueOfNewRef(self, ref, env):
        # evaluate ref value if it is an Expr
        if type(ref.expr) is self.__caseon__:
            ref.expr = self.valueOf(ref.expr, env)
        # Return the ref cell as is - upto caller to use 
        # this reference and the value in it as it sees fit
        return ref

    @case("deref")
    def valueOfDeRef(self, deref, env):
        ref = self(deref.expr, env)
        assert type(ref) is NewRefExpr
        return ref.expr

    @case("setref")
    def valueOfSetRef(self, setref, env):
        val1 = self(setref.ref, env)
        val2 = self(setref.value, env)
        assert type(val1) is NewRefExpr
        val1.expr = val2
        return val2

    @case("block")
    def valueOfBlock(self, block, env):
        value = self.__caseon__.as_num(0)
        for expr in block.exprs:
            value = self(expr, env)
        return value
