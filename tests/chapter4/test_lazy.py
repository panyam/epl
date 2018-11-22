
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter4 import lazylang
from epl.common import DefaultEnv as Env
from tests.parser.utils import parse

Expr = lazylang.Expr
Eval = lazylang.Eval

def runtest(input, exp, env = None):
    env = env or Env()
    expr,tree = parse(input, Expr)
    assert Eval().valueOf(expr, env) == exp

def test_lazy():
    input = """
        letrec infiniteloop(x) = ' ( infiniteloop(x,1) )
            in let f = proc(z) 11
                in (f (infiniteloop 0))
    """
    runtest(input, 11)
