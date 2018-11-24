
from ipdb import set_trace
from epl.chapter3 import letlang
from tests.utils import runevaltest
from tests.chapter3 import cases

Expr = letlang.Expr
Eval = letlang.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

def test_num():
    runtest(*(cases.letlang["num"]))

def test_var():
    runtest(*(cases.letlang["var"]), x = 5)

def test_zero_true():
    runtest(*(cases.letlang["isz_true"]))

def test_zero_false():
    runtest(*(cases.letlang["isz_false"]))

def test_diff():
    runtest(*(cases.letlang["diff"]), i = 1, v = 5, x = 10)

def test_if():
    runtest(*(cases.letlang["if"]), x = 33, y = 22)

def test_let():
    runtest(*(cases.letlang["let"]))

def test_letnested():
    runtest(*(cases.letlang["letnested"]))

def test_let3():
    runtest(*(cases.letlang["let3"]))

def test_letmultiargs():
    runtest(*(cases.letlang["letmultiargs"]))

