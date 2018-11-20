
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter3 import proclang
from epl.common import DefaultEnv as Env
from tests.parser.utils import parse

Expr = proclang.Expr
Eval = proclang.Eval

def runtest(input, exp, env = None):
    env = env or Env()
    expr,tree = parse(input, Expr)
    assert Eval().valueOf(expr, env) == exp

def test_basic():
    input = """ let f = proc (x) -(x,11) in (f (f 77)) """
    runtest(input, 55)

def test_basic2():
    input = """
    let x = 200 in
        let f = proc(z) -(z,x) in
            let x = 100 in
                let g = proc(z) -(z,x) in
                    -((f 1), (g 1))
    """
    runtest(input, -100)

def test_multiargs():
    input = """
        let f = proc(x,y) -(x,y) in
            -((f 1 10), (f 10 5))
    """
    runtest(input, -14)
