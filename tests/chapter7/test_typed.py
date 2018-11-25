

from ipdb import set_trace
import pytest
from epl.bp import eprint
from epl.chapter5 import trylang
from epl.chapter7 import typed
from tests import externs
from tests.utils import runevaltest
from tests.chapter7 import cases

Expr = trylang.Expr

def runtest(input, exp, **extra_env):
    from epl.env import DefaultEnv as Env
    starting_env = Env().set(**externs.contenv())
    return runevaltest(Expr, Eval, input, exp, starting_env, **extra_env)

@pytest.mark.parametrize("input, expected", cases.exceptions.values())
def _test_lazy(input, expected):
    runtest(input, expected)

