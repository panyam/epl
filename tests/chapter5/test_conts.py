
from ipdb import set_trace
from epl.utils import eprint
from epl.chapter4 import lazylang
from epl.chapter5 import continuations
from tests import externs
from tests.utils import runevaltest

Expr = lazylang.Expr
Eval = continuations.Eval

def runtest(input, exp, **extra_env):
    from epl.env import DefaultEnv as Env
    starting_env = Env().set(**externs.contenv())
    return runevaltest(Expr, Eval, input, exp, starting_env, **extra_env)

def test_factorial():
    input = """
        letrec fact(n) = if (isz n) then 1 else * (n, (fact -(n, 1)))
        in
        (fact 4)
    """
    runtest(input, 24)

def test_lazy():
    input = """
        letrec infinite-loop(x) = ' ( infinite-loop(x,1) )
            in let f = proc(z) 11
                in (f (infinite-loop 0))
    """
    runtest(input, 11)

def test_oddeven_exp():
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

def test_oddeven_imp():
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

def test_callbyref():
    input = """
        let a = 3
        in let b = 4
            in let swap = proc(x,y)
                            let temp = deref(x)
                            in begin
                                setref(x, deref(y));
                                setref(y,temp)
                            end
                in begin ((swap ref a) ref b) ; -(a,b) end
    """
    runtest(input, 1)

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

def test_callbyref():
    input = """
        let a = 3
        in let b = 4
            in let swap = proc(x,y)
                            let temp = deref(x)
                            in begin
                                setref(x, deref(y));
                                setref(y,temp)
                            end
                in begin ((swap ref a) ref b) ; -(a,b) end
    """
    runtest(input, 1)

