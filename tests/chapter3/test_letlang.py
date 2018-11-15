
from ipdb import set_trace
from epl.chapter3 import letlang
from epl.common import DefaultEnv as Env

Expr = letlang.Expr
as_let = Expr.as_let
as_num = Expr.as_number
as_if = Expr.as_if
as_diff = Expr.as_diff
as_var = Expr.as_var
as_iszero = Expr.as_iszero
Eval = letlang.Eval

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
_x = as_var("x")
_y = as_var("y")
_z = as_var("z")

def test_number():
    assert as_num(3).number.value == 3

def test_var():
    assert as_var("x").var.name == "x"

def test_zero():
    expr = as_iszero(as_num(0))
    assert Eval().valueOf(expr, None)

    expr = as_iszero(as_num(1))
    assert not Eval().valueOf(expr, None)

def test_diff():
    exp1 = as_diff(as_var("x"), as_num(3))
    exp2 = as_diff(as_var("v"), as_var("i"))
    expr = as_diff(exp1, exp2)
    env = Env().set(i = 1, v = 5, x = 10)
    assert Eval().valueOf(expr, env) == 3

def test_if():
    cond = as_iszero(as_diff(as_var("x"), as_num(11)))
    exp1 = as_diff(as_var("y"), as_num(2))
    exp2 = as_diff(as_var("y"), as_num(4))
    expr = as_if(cond, exp1, exp2)

    env = Env().set(x = 33, y = 22)
    assert Eval().valueOf(expr, env) == 18

def test_let():
    body = as_diff(as_var("x"), as_num(3))
    expr = as_let(dict(x = as_num(5)), body)
    env = Env()
    assert Eval().valueOf(expr, env) == 2

def test_let2():
    expr = as_let(dict(z = as_num(5)),
            as_let(dict(x = as_num(3)),
                as_let(dict(y = as_diff(as_var("x"), as_num(1))),
                    as_let(dict(x = as_num(4)),
                        as_diff(
                            as_var("z"),
                            as_diff(as_var("x"), as_var("y")))))))
    env = Env()
    assert Eval().valueOf(expr, env) == 3

def test_let3():
    expr = as_let(dict(x = _7),
              as_let(dict(y = _2),
                as_let(dict(y = as_let(dict(x = as_diff(_x,_1)), as_diff(_x,_y))),
                        as_diff(as_diff(_x,_8), _y))
              )
           )
    env = Env()
    assert Eval().valueOf(expr, env) == -5

def test_letmultiargs():
    expr = as_let(dict(x = _7, y = _2),
                as_let(dict(y = as_let(dict(x = as_diff(_x,_1)), as_diff(_x,_y))),
                        as_diff(as_diff(_x,_8), _y))
           )
    env = Env()
    assert Eval().valueOf(expr, env) == -5

