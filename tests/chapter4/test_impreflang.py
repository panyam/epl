

from ipdb import set_trace
from epl.utils import eprint
from epl.chapter4 import impreflang
from epl.common import DefaultEnv as Env
from tests.parser.utils import parse

Expr = impreflang.Expr
Eval = impreflang.Eval

def runtest(input, exp, env = None):
    env = env or Env()
    expr,tree = parse(input, Expr)
    assert Eval().valueOf(expr, env) == exp

def test_oddeven():
    input = """
    let x = 0 in
        letrec
            even(dummy)
                = if isz(x)
                  then 1
                  else begin
                    set x = -(x,1) ;
                    (odd 888)
                  end
            odd(dummy)
                = if isz(x)
                  then 0
                  else begin
                    set x = -(x,1) ;
                    (even 888)
                  end
        in begin set x = 13 ; (odd 888) end
    """
    runtest(input, True)

def test_counter():
    input = """
        let g = let counter = 0
                in proc(dummy)
                    begin
                        set counter = -(counter, -1) ;
                        counter
                    end
        in let a = (g 11)
            in let b = (g 11)
                in -(a,b)
    """
    runtest(input, -1)

def test_recproc():
    input = """
        let times4 = 0 in
            begin
                set times4 = proc(x)
                                if isz(x)
                                then 0
                            else -((times4 -(x,1)), -4) ;
                (times4 3)
            end
    """
    runtest(input, 12)
