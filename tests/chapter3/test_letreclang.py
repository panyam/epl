
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter3 import letreclang
from epl.common import DefaultEnv as Env
from tests.parser.utils import parse

Expr = letreclang.Expr
Eval = letreclang.Eval

def runtest(input, exp, env = None):
    env = env or Env()
    expr,tree = parse(input, Expr)
    assert Eval().valueOf(expr, env) == exp

def test_double():
    input = """
            letrec double(x) = if isz(x) then 0 else - ((double -(x,1)), -2)
            in (double 6)
    """
    runtest(input, 12)

def test_oddeven():
    input = """
            letrec
                even(x) = if isz(x) then 1 else (odd -(x,1))
                odd(x) = if isz(x) then 0 else (even -(x,1))
            in (odd 13)
    """
    runtest(input, True)

def test_currying4():
    input = """
        letrec f(x,y) = if (isz y)
                        then x
                        else (f +(x,y))
        in
        (f 1 2 3 4 5 0)
    """
    runtest(input, 15)
