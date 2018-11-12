

from ipdb import set_trace
from epl.chapter3 import letreclang
from epl.common import DefaultEnv as Env

Eval = letreclang.Eval
Expr = letreclang.Expr
as_let = Expr.as_let
as_letrec = Expr.as_letrec
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

def test_double():
    expr = as_letrec({
            "double": (["x"], as_if(as_iszero(_x), _0,
                                   as_diff(as_call(as_var("double"), as_diff(_x, _1)), as_num(-2)))),
           },
           as_call(as_var("double"), _6))
    assert Eval().valueOf(expr, Env()) == 55

def test_oddeven():
    _13 = as_num(13)
    expr = as_letrec({
            "even": (["x"], as_if(as_iszero(_x), _1, as_call(as_var("odd"), as_diff(_x, _1)))),
            "odd": (["x"], as_if(as_iszero(_x), _0, as_call(as_var("even"), as_diff(_x, _1)))),
           },
           as_call(as_var("odd"), _13))
    assert Eval().valueOf(expr, Env()) == 55
