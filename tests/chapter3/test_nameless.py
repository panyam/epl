
from ipdb import set_trace
from epl.chapter3 import letreclang
from epl.chapter3 import nameless
from epl.common import DefaultEnv as Env
from tests.parser.utils import parse

Expr = letreclang.Expr
Eval = letreclang.Eval
NExpr = nameless.Eval
NEval = nameless.Eval
NTrans = nameless.Translator

def runtest(input, value, env = None):
    env = env or Env()
    expr,tree = parse(input, Expr)
    v1 = Eval().valueOf(expr, env)
    assert v1 == value

    nexpr = NTrans().translate(expr)
    v2 = NEval().valueOf(nexpr)
    assert v2 == value

def test_nameless1():
    input = "let x = 3 in x"
    runtest(input, 3)
