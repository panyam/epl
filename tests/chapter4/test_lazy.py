
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter4 import lazylang
from tests.utils import runevaltest

Expr = lazylang.Expr
Eval = lazylang.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

def test_lazy():
    input = """
        letrec infiniteloop(x) = ' ( infiniteloop(x,1) )
            in let f = proc(z) 11
                in (f (infiniteloop 0))
    """
    runtest(input, 11)
