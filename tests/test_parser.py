
from ipdb import set_trace
from epl.utils import eprint
from tests.parserutils import parse
from epl.chapter3.letreclang import Expr

def runtest(input, exp):
    e,t = parse(input, Expr)
    assert e == exp

def test_parse_num():
    runtest("3", Expr.as_num(3))

def test_parse_varname():
    runtest("x", Expr.as_var("x"))

def test_parse_paren():
    runtest("( ( ( 666 )) )", Expr.as_num(666))

def test_operators():
    runtest("+ (x, y)", Expr.as_call(Expr.as_var("+"),
            Expr.as_tup(Expr.as_var("x"), Expr.as_var("y"))))
    runtest(">>(x,y)", Expr.as_call(Expr.as_var(">>"),
            Expr.as_tup(Expr.as_var("x"), Expr.as_var("y"))))

def test_parse_iszero():
    runtest("? ( 0 )",
        Expr.as_call(Expr.as_var("?"), Expr.as_num(0)))

def test_parse_iszero_cust():
    e2 = Expr.as_iszero(Expr.as_num(33))
    runtest("isz ( ( ( 33 ) ) )", e2)

def test_parse_diff():
    e2 = Expr.as_diff(Expr.as_num(33), Expr.as_num(44))
    runtest("- ( 33, 44)", e2)

def test_parse_tuple():
    e2 = Expr.as_call(Expr.as_var("+"),
                Expr.as_tup(Expr.as_num(3), Expr.as_num(4)))
    runtest("+ (3, 4)", e2)

def test_parse_letrec_double():
    e2 = Expr.as_letrec({
        "double": Expr.as_proc(["x"],
                    Expr.as_if(Expr.as_iszero(Expr.as_var("x")),
                               Expr.as_num(0),
                               Expr.as_diff(
                                   Expr.as_call(Expr.as_var("double"),
                                                Expr.as_diff(
                                                    Expr.as_var("x"),
                                                    Expr.as_num(1))),
                                   Expr.as_num(-2)))).procexpr
        }, Expr.as_call(Expr.as_var("double"), Expr.as_num(6)))
    runtest("""
        letrec
            double(x) = (if (isz x) then 0 else -((double -(x,1)), -2))
        in (double 6)
    """, e2)


def test_parse_letrec_oddeven():
    even = Expr.as_proc(["x"],
                Expr.as_if(
                    Expr.as_iszero(Expr.as_var("x")),
                    Expr.as_num(1),
                    Expr.as_call(
                        Expr.as_var("odd"),
                            Expr.as_diff(
                                Expr.as_var("x"),
                                Expr.as_num(1))))).procexpr
    odd = Expr.as_proc(["x"],
                Expr.as_if(
                    Expr.as_iszero(Expr.as_var("x")),
                    Expr.as_num(0),
                    Expr.as_call(
                        Expr.as_var("even"),
                            Expr.as_diff(
                                Expr.as_var("x"),
                                Expr.as_num(1))))).procexpr
    e2 = Expr.as_letrec({"even": even, "odd": odd},
            Expr.as_call(Expr.as_var("odd"), Expr.as_num(13)))
    runtest("""
        letrec
            even(x) = if (isz x) then 1 else (odd -(x,1))
            odd(x) = if (isz x) then 0 else (even -(x,1))
        in (odd 13)
    """, e2)
