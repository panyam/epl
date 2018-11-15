

from ipdb import set_trace
from epl.chapter3 import proclang
from epl.common import DefaultEnv as Env

Eval = proclang.Eval
Expr = proclang.Expr
as_let = Expr.as_let
as_num = Expr.as_number
as_if = Expr.as_if
as_diff = Expr.as_diff
as_var = Expr.as_var
as_iszero = Expr.as_iszero
as_proc = Expr.as_proc
as_call = Expr.as_call

# Some literals to ease things
_0 = as_num(0)
_1 = as_num(1)
_2 = as_num(2)
_3 = as_num(3)
_4 = as_num(4)
_5 = as_num(5)
_6 = as_num(6)
_7 = as_num(7)
_8 = as_num(8)
_9 = as_num(9)
_10 = as_num(10)
_11 = as_num(11)
_f = as_var("f")
_g = as_var("g")
_x = as_var("x")
_y = as_var("y")
_z = as_var("z")

def test_basic():
    _77 = as_num(77)
    expr = as_let(dict(f = as_proc("x", as_diff(_x, _11))),
                  as_call(_f, as_call(_f, _77)))
    assert Eval().valueOf(expr, Env()) == 55

def test_basic2():
    _100 = as_num(100)
    _200 = as_num(200)
    expr = as_let(dict(x = _200),
                  as_let(dict(f = as_proc("z", as_diff(_z, _x))),
                         as_let(dict(x = _100),
                                as_let(dict(g = as_proc("z", as_diff(_z, _x))),
                                       as_diff(as_call(_f, _1), as_call(_g, _1))))))
    assert Eval().valueOf(expr, Env()) == -100

def test_multiargs():
    expr = as_let(dict(f = as_proc(["x", "y"], as_diff(_x, _y))),
                  as_diff(as_call(_f, _1, _10), as_call(_f, _10, _5)))
    assert Eval().valueOf(expr, Env()) == -14

