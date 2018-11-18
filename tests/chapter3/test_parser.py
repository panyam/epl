
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
    e = parse("isz ( ( ( 33 ) ) )")
    assert e.is_call
    callexpr, rator, rargs = e.callexpr, e.callexpr.operator, e.callexpr.args
    assert rator.is_var and rator.var.name == "isz"
    assert rargs[0].is_number and rargs[0].number.value == 33

def test_parse_diff():
    e = parse("- ( ( ( 33 ) ) ) 44")
    assert e.is_call
    callexpr, rator, rargs = e.callexpr, e.callexpr.operator, e.callexpr.args
    assert rator.is_var and rator.var.name == "-"
    assert rargs[0].is_number and rargs[0].number.value == 33
    assert rargs[1].is_number and rargs[1].number.value == 44

def test_parse_tuple():
    e = parse("- (3, 4)")
    e2 = Expr.as_call(Expr.as_var("-"),
                Expr.as_tup(Expr.as_number(3), Expr.as_number(4)))
    assert e == e2

def test_parse_if():
    e = parse("if isz 0 then 1 else 2")
    assert e.is_if
    cond,exp1,exp2 = e.ifexpr.cond,e.ifexpr.exp1,e.ifexpr.exp2
    assert cond.is_call
    assert cond.callexpr.operator.is_var and cond.callexpr.operator.var.name == "isz"
    assert cond.callexpr.args[0].is_number and cond.callexpr.args[0].number.value == 0
    assert exp1.is_number and exp1.number.value == 1
    assert exp2.is_number and exp2.number.value == 2
