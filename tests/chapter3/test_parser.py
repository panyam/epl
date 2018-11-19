
from ipdb import set_trace
from epl.chapter3.utils import eprint
from tests.chapter3.parserutils import parse, Expr

def runtest(input, expected):
    e = parse(input)
    assert e == expected

def test_parse_let_double():
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
            some(x) = proc (y,z) (- ((* y x), 1))
        in (double 6)
    """, e2)
    # double(x) = (if (isz x) then 0 else -((double -(x,1)), -2))

