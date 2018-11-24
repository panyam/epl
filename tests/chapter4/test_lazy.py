
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter4 import lazylang
from tests.utils import runevaltest
from tests.chapter4 import cases

Expr = lazylang.Expr
Eval = lazylang.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

def test_lazy():
    runtest(*(cases.lazy["infinite"]))
