
from epl.unions import *

class Number(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<Num(%d)>" % self.value

class VarExpr(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Var(%s)>" % self.name

class IsZeroExpr(object):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return "<IsZero(%s)>" % str(self.expr)

class DiffExpr(object):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

    def __repr__(self):
        return "<Diff(%s, %s)>" % (str(self.exp1), str(self.exp2))

class IfExpr(object):
    def __init__(self, condition, exp1, exp2):
        self.condition = condition
        self.exp1 = exp1
        self.exp2 = exp2

    def __repr__(self):
        return "<If(%s) { %s } else { %s }>" % (str(self.condition), str(self.exp1), str(self.exp2))

class LetExpr(object):
    def __init__(self, mappings, body):
        self.mappings = mappings
        self.body = body

    def __repr__(self):
        return "<Let (%s) in %s" % (", ".join(("%s = %s" % k,repr(v)) for k,v in self.mappings.items()), repr(self.body))

class Expr(Union):
    # Convert this into a union metaclass
    number = Variant(Number)
    var = Variant(VarExpr)
    diff = Variant(DiffExpr)
    iszero = Variant(IsZeroExpr)
    ifexpr = Variant(IfExpr, checker = "is_if", constructor = "as_if")
    letexpr = Variant(LetExpr, checker = "is_let", constructor = "as_let")

class Eval(CaseMatcher):
    # Tells which union type we are "case matching" on
    __caseon__ = Expr

    # These names MUST match the different cases in our "union_type"
    def valueOf(self, expr, env):
        # We expect the signature of "valueOf" and each selected
        # subexpression to have the same arity and return type
        return self(expr, env)
        # func, child = self.select(expr)
        # return func(self, child, env)

    @case("number")
    def valueOfNumber(self, number, env = None):
        return number.value

    @case("var")
    def valueOfVar(self, var, env):
        return env.get(var.name)

    @case("diff")
    def valueOfDiff(self, diff, env):
        val1 = self.valueOf(diff.exp1, env)
        val2 = self.valueOf(diff.exp2, env)
        return val1 - val2

    @case("iszero")
    def valueOfIsZero(self, iszero, env):
        return self.valueOf(iszero.expr, env) == 0

    @case("ifexpr")
    def valueOfIf(self, ifexpr, env):
        result = self.valueOf(ifexpr.condition, env)
        return self.valueOf(ifexpr.exp1 if result else ifexpr.exp2, env)

    @case("letexpr")
    def valueOfLet(self, letexpr, env):
        expvals = {var: self.valueOf(exp, env) for var,exp in letexpr.mappings.items()}
        newenv = env.extend(**expvals)
        return self.valueOf(letexpr.body, newenv)

