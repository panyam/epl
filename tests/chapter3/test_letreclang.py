
from ipdb import set_trace
from epl import bp
from epl.bp import eprint
from epl.chapter3 import letreclang
from tests.utils import runevaltest
from tests.chapter3 import cases

Expr = letreclang.Expr
Eval = letreclang.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

def test_double():
    runtest(*(cases.letreclang["double"]))

def test_oddeven():
    runtest(*(cases.letreclang["oddeven"]))

def test_currying():
    runtest(*(cases.letreclang["currying"]))

