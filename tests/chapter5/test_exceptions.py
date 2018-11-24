
from ipdb import set_trace
from epl.bp import eprint
from epl.chapter5 import trylang
from tests import externs
from tests.utils import runevaltest

Expr = trylang.Expr
Eval = trylang.Eval

def runtest(input, exp, **extra_env):
    from epl.env import DefaultEnv as Env
    starting_env = Env().set(**externs.contenv())
    return runevaltest(Expr, Eval, input, exp, starting_env, **extra_env)

