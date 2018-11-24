
from epl import bp
from epl.unions import *
from epl.common import Lit

class VarExpr(object):
    def __init__(self, name):
        self.name = name

    def printables(self):
        yield 0, "var %s" % self.name

    def __eq__(self, another):
        return self.name == another.name

    def __repr__(self):
        return "<Var(%s)>" % self.name

class TupleExpr(object):
    def __init__(self, *children):
        self.children = list(children)

    def printables(self):
        yield 0, "Tuple:"
        for c in self.children:
            yield 1, c.printables()

    def __eq__(self, another):
        if len(self.children) != len(another.children):
            return False
        for e1,e2 in zip(self.children, another.children):
            if e1 != e2: return False
        return True

    def __repr__(self):
        return "<Tuple(%s)>" % ", ".join(map(repr, self.children))

class IsZeroExpr(object):
    def __init__(self, expr):
        self.expr = expr

    def printables(self):
        yield 0, "IsZero:"
        yield 1, self.expr.printables()

    def __repr__(self):
        return "<IsZero(%s)>" % str(self.expr)

    def __eq__(self, another):
        return self.expr == another.expr

class OpExpr(object):
    def __init__(self, op, *exprs):
        self.op = op
        if exprs and len(exprs) == 1 and type(exprs[0]) is list:
            self.exprs = exprs[0]
        else:
            self.exprs = list(exprs)

    def printables(self):
        yield 0, "Op (%s):" % self.op
        for exp in self.exprs:
            yield 1, exp.printables()

    def __eq__(self, another):
        return self.op == another.op and \
               self.exprs == another.exprs

    def __repr__(self):
        return "<Op(%s, [%s])>" % (self.op, ", ".join(map(repr, self.exprs)))

class IfExpr(object):
    def __init__(self, cond, exp1, exp2):
        self.cond = cond
        self.exp1 = exp1
        self.exp2 = exp2

    def printables(self):
        yield 0, "If:"
        yield 1, "Cond"
        yield 2, self.cond.printables()
        yield 1, "Then"
        yield 2, self.exp1.printables()
        yield 1, "Else"
        yield 2, self.exp2.printables()

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

    def printables(self):
        yield 0, "Let:"
        for k,v in self.mappings.items():
            yield 2, "%s = " % k
            yield 3, v.printables()
        yield 1, "in:"
        yield 2, self.body.printables()

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
    lit = Variant(Lit)
    var = Variant(VarExpr)
    opexpr = Variant(OpExpr)
    tupexpr = Variant(TupleExpr, checker = "is_tup", constructor = "as_tup")
    iszero = Variant(IsZeroExpr)
    ifexpr = Variant(IfExpr, checker = "is_if", constructor = "as_if")
    let = Variant(LetExpr, checker = "is_let", constructor = "as_let")

    @classmethod
    def as_diff(cls, e1, e2):
        return cls.as_opexpr("-", e1, e2)

    def __eq__(self, another):
        v1,v2 = self.variant_value, another.variant_value
        return type(v1) == type(v2) and v1 == v2

    def printables(self):
        yield 0, self.variant_value.printables()

class Eval(CaseMatcher):
    # Tells which union type we are "case matching" on
    __caseon__ = Expr

    # These names MUST match the different cases in our "union_type"
    def valueOf(self, expr, env):
        # We expect the signature of "valueOf" and each selected
        # subexpression to have the same arity and return type
        return self(expr, env)

    @case("lit")
    def valueOfLit(self, lit, env = None):
        return lit

    @case("var")
    def valueOfVar(self, var, env):
        return env.get(var.name)

    @case("opexpr")
    def valueOfOpExpr(self, opexpr, env):
        # In this lang we make "op" expressions just hooks to external plugins
        # We can get even more generic once we have procedures (proclang onwards)
        opfunc = env.get(opexpr.op)
        assert opfunc is not None, "No plug in found for operator: %s" % opexpr.op
        return opfunc(self, env, opexpr.exprs)

    @case("tupexpr")
    def valueOfTUple(self, tupexpr, env):
        values = [self.valueOf(v,env) for v in tupexpr.children]
        return TupleExpr(*values)

    @case("iszero")
    def valueOfIsZero(self, iszero, env):
        return Lit(self.valueOf(iszero.expr, env).value == 0)

    @case("ifexpr")
    def valueOfIf(self, ifexpr, env):
        result = self.valueOf(ifexpr.cond, env).value
        return self.valueOf(ifexpr.exp1 if result else ifexpr.exp2, env)

    @case("let")
    def valueOfLet(self, let, env):
        expvals = {var: self.valueOf(exp, env) for var,exp in let.mappings.items()}
        newenv = env.extend(**expvals)
        return self.valueOf(let.body, newenv)

