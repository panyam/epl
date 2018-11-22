
from ipdb import set_trace
from epl.env import DefaultEnv as Env
from tests import externs
from tests.parser.utils import parse

def default_env():
    return Env().set(**externs.env()).push()

def runevaltest(Expr, Eval, input, exp, **extra_env):
    newenv = default_env().set(**extra_env)
    expr,tree = parse(input, Expr)
    assert Eval().valueOf(expr, newenv) == exp
