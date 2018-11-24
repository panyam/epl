
from epl.env import DefaultEnv as Env
from epl.bp import eprint
from tests import externs
from tests.parser.utils import parse

def default_env():
    return Env().set(**externs.env())

def runevaltest(Expr, Eval, input, exp, starting_env = None, **extra_env):
    starting_env = starting_env or default_env()
    newenv = starting_env.push().set(**extra_env)
    expr,tree = parse(input, Expr)
    value = Eval().valueOf(expr, newenv)
    assert value == exp
