
from ipdb import set_trace
from epl.chapter3 import letlang
from epl.common import DefaultEnv as Env
from tests.parser.utils import parse

Expr = letlang.Expr
Eval = letlang.Eval

def runtest(input, exp, env = None):
    env = env or Env()
    expr,tree = parse(input, Expr)
    assert Eval().valueOf(expr, env) == exp

def test_num():
    runtest("""3""", 3)

def test_var():
    runtest("""x""", 5, Env().set(x = 5))

def test_zero():
    runtest("isz 0", True)
    runtest("isz 1", False)

def test_diff():
    env = Env().set(i = 1, v = 5, x = 10)
    runtest("-(-(x,3),-(v,i))", 3, env)

def test_if():
    input = " if isz -(x,11) then -(y,2) else -(y,4) "
    env = Env().set(x = 33, y = 22)
    runtest(input, 18, env)

def test_let():
    input = "let x = 5 in -(x,3)"
    runtest(input, 2)

def test_let2():
    input = "let z = 5 in let x = 3 in let y = -(x, 1) in let x = 4 in -(z, -(x,y))"
    runtest(input, 3)

def test_let3():
    input = """
        let x = 7 in
            let y = 2 in
                let y = let x = -(x,1) in -(x,y)
                in -(-(x,8), y)
    """
    runtest(input, -5)

def test_letmultiargs():
    input = """
        let x = 7 y = 2 in
            let y = let x = -(x,1) in -(x,y)
            in -(-(x, 8),y)
    """
    runtest(input, -5)

