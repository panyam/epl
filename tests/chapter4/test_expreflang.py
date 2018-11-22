
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter4 import expreflang
from tests.utils import runevaltest

Expr = expreflang.Expr
Eval = expreflang.Eval

def runtest(input, exp, **extra_env):
    return runevaltest(Expr, Eval, input, exp, **extra_env)

def test_oddeven():
    input = """
    let x = newref(0) in
        letrec
            even(dummy)
                = if isz(deref(x))
                  then 1
                  else begin
                    setref(x, -(deref(x), 1));
                    (odd 888)
                  end
            odd(dummy)
                = if isz(deref(x))
                  then 0
                  else begin
                    setref(x, -(deref(x), 1));
                    (even 888)
                  end
        in begin setref(x, 13) ; (odd 888) end
    """
    runtest(input, True)

def test_counter():
    input = """
        let g = let counter = newref(0)
                in proc(dummy)
                    begin
                        setref(counter, -(deref(counter), -1)) ;
                        deref(counter)
                    end
        in let a = (g 11)
            in let b = (g 11)
                in -(a,b)
    """
    runtest(input, -1)

