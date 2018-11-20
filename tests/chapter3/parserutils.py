
from ipdb import set_trace
from epl import parser

# "Custom" functions are just "calls" as macros!!!
def isz_maker(params, Expr):
    # we need atleast 1 arg
    assert len(params) >= 1
    return Expr.as_iszero(params[0])

def diff_maker(params, Expr):
    # we need atleast 2 args
    assert len(params) >= 1
    assert params[0].is_tup
    children = params[0].tupexpr.children
    assert len(children) == 2
    return Expr.as_diff(children[0], children[1])

optable = {
    "isz": (1, isz_maker),
    "-": (1, diff_maker)
}

def parse(input, Expr):
    return parser.parse(input, Expr, optable)
