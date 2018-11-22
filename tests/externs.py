
import functools

# "Custom" functions are just "calls" as macros!!!
def env():
    def isz_expr_eval(evalfunc, env, exprs):
        return evalfunc(exprs[0], env) == 0

    def minus_expr_eval(evalfunc, env, exprs):
        val1 = evalfunc(exprs[0], env)
        val2 = evalfunc(exprs[1], env)
        return val1 - val2

    def div_expr_eval(evalfunc, env, exprs):
        val1 = evalfunc(exprs[0], env)
        val2 = evalfunc(exprs[1], env)
        return val1 / val2

    def plus_expr_eval(evalfunc, env, exprs):
        vals = [evalfunc(exp, env) for exp in exprs]
        return sum(vals)

    def mult_expr_eval(evalfunc, env, exprs):
        vals = [evalfunc(exp, env) for exp in exprs]
        return functools.reduce(lambda x,y: x*y, vals, 1)

    return {
        "isz": isz_expr_eval,
        "+": plus_expr_eval,
        "-": minus_expr_eval,
        "/": div_expr_eval,
        "*": mult_expr_eval,
    }
