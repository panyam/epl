
from ipdb import set_trace
from epl import parser

# "Custom" functions are just "calls" as macros!!!
def isz_maker(params, Expr):
    # we need atleast 1 arg
    assert len(params) >= 1
    return Expr.as_iszero(params[0])

def assert_tuplen(params, n):
    assert len(params) >= 1
    assert params[0].is_tup
    children = params[0].tupexpr.children
    assert len(children) == n
    return children

def diff_maker(params, Expr):
    # we need atleast 2 args
    children = assert_tuplen(params, 2)
    return Expr.as_diff(children[0], children[1])

def setref_maker(params, Expr):
    children = assert_tuplen(params, 2)
    return Expr.as_setref(children[0], children[1])

def deref_maker(params, Expr):
    assert len(params) >= 1
    return Expr.as_deref(params[0])

def newref_maker(params, Expr):
    assert len(params) >= 1
    return Expr.as_newref(params[0])

optable = {
    "isz": (1, isz_maker),
    "-": (1, diff_maker),
    "setref": (1, setref_maker),
    "deref": (1, deref_maker),
    "newref": (1, newref_maker)
}

def parse(input, Expr):
    return parser.parse(input, Expr, optable)
