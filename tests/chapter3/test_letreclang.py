

from ipdb import set_trace
from epl.chapter3 import letreclang
from epl.common import DefaultEnv as Env
from tests.chapter3.parserutils import parse

Eval = letreclang.Eval

def test_double():
    expr,tree = parse("""
            letrec double(x) = if isz(x) then 0 else - ((double -(x,1)), -2)
            in (double 6)
            """)
    assert Eval().valueOf(expr, Env()) == 12

def test_oddeven():
    expr,tree = parse ("""
            letrec
                even(x) = if isz(x) then 1 else (odd -(x,1))
                odd(x) = if isz(x) then 0 else (even -(x,1))
            in (odd 13)
            """)
    assert Eval().valueOf(expr, Env()) == True
