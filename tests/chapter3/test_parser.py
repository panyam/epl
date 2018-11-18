
from ipdb import set_trace
from epl.chapter3 import parser
from epl.chapter3 import letreclang

# "Custom" functions are just "calls" as macros!!!
optable = {
    "isz": lambda arg: letreclang.Expr.as_iszero(arg),
    "-": lambda arg1, arg2: letreclang.Expr.as_diff(arg1, arg2)
}

Expr = letreclang.Expr

def parse(input):
    return parser.parse(input, Expr)

def runtest(input, expected):
    e = parse(input)
    assert e == expected

def test_parse_number():
    runtest("3", Expr.as_number(3))

def test_parse_varname():
    runtest("x", Expr.as_var("x"))

def test_parse_paren():
    runtest("( ( ( 666 )) )", Expr.as_number(666))

def test_operators():
    runtest("-", Expr.as_var("-"))

def test_parse_iszero():
    runtest("? ( 0 )",
        Expr.as_call(Expr.as_var("?"), Expr.as_number(0)))

def test_parse_iszero_cust():
    e2 = Expr.as_call(Expr.as_var("isz"), Expr.as_number(33))
    runtest("isz ( ( ( 33 ) ) )", e2)

def test_parse_diff():
    e2 = Expr.as_call(Expr.as_var("-"), Expr.as_number(33), Expr.as_number(44))
    runtest("- ( ( ( 33 ) ) ) 44", e2)

def test_parse_tuple():
    e2 = Expr.as_call(Expr.as_var("-"),
                Expr.as_tup(Expr.as_number(3), Expr.as_number(4)))
    runtest("- (3, 4)", e2)

def test_parse_if():
    e2 = Expr.as_if(Expr.as_call(Expr.as_var("isz"), Expr.as_number(0)),
            Expr.as_number(1), Expr.as_number(2))
    runtest("if isz 0 then 1 else 2", e2)
