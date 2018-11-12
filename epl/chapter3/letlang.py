
from constructs import *

class Expr(Union):
    # Convert this into a union metaclass
    number = Variant(Number)
    var = Variant(VarExpr)
    diff = Variant(DiffExpr)
    zero = Variant(ZeroExpr)
    ifexpr = Variant(IfExpr, checker_name = "is_if")
    letexpr = Variant(LetExpr, checker_name = "is_let")

class Eval(CaseMatcher):
    # Tells which union type we are "case matching" on
    __caseon__ = Expr

    # These names MUST match the different cases in our "union_type"
    def valueOf(self, expr, env):
        # We expect the signature of "valueOf" and each selected
        # subexpression to have the same arity and return type
        func, child = self.select(expr)
        return func(child, env)

    @case("number")
    def valueOfNumber(self, number, env = None):
        return number.value

    @case("var")
    def valueOfVar(self, var, env):
        return env.get(var.name)

    @case("diff")
    def valueOfDiff(self, diff, env):
        return self.valueOf(diff.exp1, env) - self.valueOf(diff.exp2, env)

    @case("zero")
    def valueOfZero(self, zero, env):
        return self.valueOf(zero.expr, env) == 0

    @case("ifexpr")
    def valueOfIf(self, ifexpr, env):
        result = self.valueOf(ifexpr.condition, env)
        return self.valueOf(ifexpr.exp1 if result == 0 else ifexpr.exp2, env)

    @case("letexpr")
    def valueOfLet(self, letexpr, env):
        expvals = {var: self.valueOf(exp, env) for exp in letexpr.mappings.items()}
        newenv = env.extend(**expvals)
        return self.valueOf(letexpr.body, newenv)

