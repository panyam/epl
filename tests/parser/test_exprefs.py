

from ipdb import set_trace
from epl.utils import eprint
from tests.parser.utils import parse
from epl.chapter4.expreflang import Expr

def runtest(input, exp):
    e,t = parse(input, Expr)
    set_trace()
    assert e == exp
