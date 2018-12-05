
import taggedunion
from epl import bp
from epl.chapter7 import typed
from tests import externs
from tests import settings
from tests.utils import parse, runevaltest, prepareenv

def runtest(input, exp, starting_env = None, **extra_env):
    Expr = settings.get("Expr")
    Type = settings.get("Type")
    TypeOf = settings.get("TypeOf")
    expr,tree = parse(input, Expr, Type)
    if settings.get("print_tree", no_throw = True):
        bp.eprint(expr)
    env = prepareenv(starting_env, **extra_env)
    try:
        foundtype = TypeOf()(expr, env)
        if type(exp) is not bool:
            assert foundtype == exp
    except taggedunion.InvalidVariantError as ive:
        assert exp == False
    except typed.TypeError as te:
        assert exp == False
