

from ipdb import set_trace
import pytest
from epl.bp import eprint
from epl.chapter5 import trylang
from epl.chapter5 import continuations
from tests import externs
from tests.utils import runevaltest
from tests.chapter5 import cases

Expr = trylang.Expr
Eval = continuations.Eval

def runtest(input, exp, **extra_env):
    from epl.env import DefaultEnv as Env
    starting_env = Env().set(**externs.contenv())
    return runevaltest(Expr, Eval, input, exp, starting_env, **extra_env)

@pytest.mark.parametrize("input, expected", cases.exceptions.values())
def test_lazy(input, expected):
    runtest(input, expected)

