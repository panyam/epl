
from epl import bp
from epl.bp import eprint
from epl.chapter4 import expreflang
from tests.utils import runevaltest
from tests.chapter4 import cases

Expr = expreflang.Expr
Eval = expreflang.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

def test_oddeven():
    runtest(*(cases.exprefs["oddeven"]))

def test_counter():
    runtest(*(cases.exprefs["counter"]))

