
from ipdb import set_trace
import pytest
from epl.bp import eprint
from epl.chapter4 import lazylang
from epl.chapter5 import continuations
from tests import externs
from tests.utils import runevaltest
from tests.chapter4 import cases

Expr = lazylang.Expr
Eval = continuations.Eval

def runtest(input, exp, **extra_env):
    from epl.env import DefaultEnv as Env
    starting_env = Env().set(**externs.contenv())
    return runevaltest(Expr, Eval, input, exp, starting_env, **extra_env)

@pytest.mark.parametrize("input, expected", cases.lazy.values())
def test_lazy(input, expected):
    runtest(input, expected)

@pytest.mark.parametrize("input, expected", cases.misc.values())
def test_misc(input, expected):
    runtest(input, expected)

@pytest.mark.parametrize("input, expected", cases.exprefs.values())
def test_exprefs(input, expected):
    runtest(input, expected)

@pytest.mark.parametrize("input, expected", cases.imprefs.values())
def test_imprefs(input, expected):
    runtest(input, expected)

