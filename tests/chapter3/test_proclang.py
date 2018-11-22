
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter3 import proclang
from tests.utils import runevaltest

Expr = proclang.Expr
Eval = proclang.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

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

def test_currying2():
    input = """ let f = proc(x,y) -(x,y) in ((f 5) 3) """
    runtest(input, 2)

def test_currying3():
    input = """
        let f = proc(x,y)
                if (isz y)
                then x
                else proc(a,b) (if isz b then +(a,x,y) else +(a,b,x,y))
        in
        (f 1 2 2 0)
    """
    runtest(input, 5)

