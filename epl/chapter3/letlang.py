
from epl.unions import *
from epl.chapter3.constructs import *

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
        func, child = self.select(expr)
        return func(self, child, env)

    @case("number")
    def valueOfNumber(self, number, env = None):
        return number.value

    @case("var")
    def valueOfVar(self, var, env):
        return env.get(var.name)

    @case("diff")
    def valueOfDiff(self, diff, env):
        return self.valueOf(diff.exp1, env) - self.valueOf(diff.exp2, env)

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

