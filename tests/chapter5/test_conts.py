
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter4 import lazylang
from epl.chapter5 import continuations
from tests import externs
from tests.utils import runevaltest

Expr = lazylang.Expr
Eval = continuations.Eval

def runtest(input, exp, **extra_env):
    from epl.env import DefaultEnv as Env
    starting_env = Env().set(**externs.contenv())
    return runevaltest(Expr, Eval, input, exp, starting_env, **extra_env)

def test_factorial():
    input = """
        letrec fact(n) = if (isz n) then 1 else * (n, (fact -(n, 1)))
        in
        (fact 4)
    """
    runtest(input, 24)

def test_lazy():
    input = """
        letrec infinite-loop(x) = ' ( infinite-loop(x,1) )
            in let f = proc(z) 11
                in (f (infinite-loop 0))
    """
    runtest(input, 11)


