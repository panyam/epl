
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter4 import lazylang
from epl.chapter5 import continuations
from tests.utils import runevaltest

Expr = lazylang.Expr
Eval = continuations.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

def test_lazy():
    input = """
        letrec infinite-loop(x) = ' ( infinite-loop(x,1) )
            in let f = proc(z) 11
                in (f (infinite-loop 0))
    """
    runtest(input, 11)
