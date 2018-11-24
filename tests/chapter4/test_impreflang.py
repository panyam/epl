
from epl import bp
from epl.bp import eprint
from epl.chapter4 import impreflang
from tests.utils import runevaltest
from tests.chapter4 import cases

Expr = impreflang.Expr
Eval = impreflang.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

def test_oddeven():
    runtest(*(cases.imprefs["oddeven"]))

def test_counter():
    runtest(*(cases.imprefs["counter"]))

def test_recproc():
    runtest(*(cases.imprefs["recproc"]))

def test_callbyref():
    runtest(*(cases.imprefs["callbyref"]))

