
from epl.unions import *

class Number(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, another):
        return self.value == another.value

    def __repr__(self):
        return "<Num(%d)>" % self.value

class VarExpr(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, another):
        return self.name == another.name

    def __repr__(self):
        return "<Var(%s)>" % self.name

class TupleExpr(object):
    def __init__(self, *children):
        self.children = list(children)

    def __eq__(self, another):
        return len(self.children) == len(another.children) and \
                all(e1 == e2 for e1,e2 in zip(self.children, another.children))

    def __repr__(self):
        return "<Tuple(%s)>" % ", ".join(map(repr, self.children))

class IsZeroExpr(object):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return "<IsZero(%s)>" % str(self.expr)

    def __eq__(self, another):
        return self.expr == another.expr

class DiffExpr(object):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

    def __eq__(self, another):
        return  self.exp1 == another.exp1 and \
                self.exp2 == another.exp2

    def __repr__(self):
        return "<Diff(%s, %s)>" % (str(self.exp1), str(self.exp2))

class IfExpr(object):
    def __init__(self, cond, exp1, exp2):
        self.cond = cond
        self.exp1 = exp1
        self.exp2 = exp2

    def __eq__(self, another):
        return  self.cond == another.cond and \
                self.exp1 == another.exp1 and \
                self.exp2 == another.exp2

    def __repr__(self):
        return "<If(%s) { %s } else { %s }>" % (str(self.cond), str(self.exp1), str(self.exp2))

class LetExpr(object):
    def __init__(self, mappings, body):
        self.mappings = mappings
        self.body = body

    def __eq__(self, another):
        return  len(self.mappings) == len(another.mappings) and \
                all(k in another.mappings and 
                    self.mappings[k] == another.mappings[k] 
                        for k in self.mappings.keys()) and \
                self.body == another.body

    def __repr__(self):
        return "<Let (%s) in %s" % (", ".join(("%s = %s" % k,repr(v)) for k,v in self.mappings.items()), repr(self.body))

class Expr(Union):
    # Convert this into a union metaclass
    number = Variant(Number)
    var = Variant(VarExpr)
    diff = Variant(DiffExpr)
    tupexpr = Variant(TupleExpr, checker = "is_tup", constructor = "as_tup")
    iszero = Variant(IsZeroExpr)
    ifexpr = Variant(IfExpr, checker = "is_if", constructor = "as_if")
    letexpr = Variant(LetExpr, checker = "is_let", constructor = "as_let")

    def __eq__(self, another):
        v1,v2 = self.variant_value, another.variant_value
        return type(v1) == type(v2) and v1 == v2

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

    @case("tupexpr")
    def valueOfTUple(self, tupexpr, env):
        values = [self.valueOf(v,env) for v in tupexpr.children]
        return TupleExpr(*values)

    @case("iszero")
    def valueOfIsZero(self, iszero, env):
        return self.valueOf(iszero.expr, env) == 0

    @case("ifexpr")
    def valueOfIf(self, ifexpr, env):
        result = self.valueOf(ifexpr.cond, env)
        return self.valueOf(ifexpr.exp1 if result else ifexpr.exp2, env)

    @case("letexpr")
    def valueOfLet(self, letexpr, env):
        expvals = {var: self.valueOf(exp, env) for var,exp in letexpr.mappings.items()}
        newenv = env.extend(**expvals)
        return self.valueOf(letexpr.body, newenv)

