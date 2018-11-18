
from ipdb import set_trace
from epl.chapter3 import parser
from epl.chapter3 import letreclang

# "Custom" functions are just "calls" as macros!!!
optable = {
    "isz": lambda arg: letreclang.Expr.as_iszero(arg),
    "-": lambda arg1, arg2: letreclang.Expr.as_diff(arg1, arg2)
}

def parse(input):
    return parser.parse(input, letreclang.Expr)

def test_parse_number():
    e = parse("3")
    assert e.is_number and e.variant_value.value == 3

def test_parse_varname():
    e = parse("x")
    assert e.is_var and e.variant_value.name == "x"

def test_parse_paren():
    e = parse("( ( ( 666 )) )")
    assert e.is_number and e.number.value == 666

def test_operators():
    e = parse("-")
    assert e.is_var and e.var.name == "-"

def test_parse_iszero():
    e = parse("? 0")
    assert e.is_call
    callexpr, rator, rargs = e.callexpr, e.callexpr.operator, e.callexpr.args
    assert rator.is_var and rator.var.name == "?"
    assert rargs[0].is_number and rargs[0].number.value == 0

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
