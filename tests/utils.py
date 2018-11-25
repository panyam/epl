
from epl import parser
from epl.env import DefaultEnv as Env
from epl.bp import eprint
from tests import externs

def default_env():
    return Env().set(**externs.env())

def parse(input, expr_class, optable = None):
    mixins = [  parser.BasicMixin, parser.ProcMixin, parser.LetMixin,
                parser.LetRecMixin, parser.RefMixin, parser.TryMixin, parser.TypingMixin ]
    theparser = parser.make_parser(expr_class, optable, *mixins)
    return theparser.parse(input)

def runevaltest(Expr, Eval, input, exp, starting_env = None, **extra_env):
    starting_env = starting_env or default_env()
    newenv = starting_env.push().set(**extra_env)
    expr,tree = parse(input, Expr)
    value = Eval().valueOf(expr, newenv)
    assert value == exp
