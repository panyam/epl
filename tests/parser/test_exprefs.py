

from ipdb import set_trace
from epl.utils import eprint
from tests.parser.utils import parse
from epl.chapter4.expreflang import Expr

def runtest(input, exp):
    e,t = parse(input, Expr)
    set_trace()
    assert e == exp

def test_parse():
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
            even(dummy)
                = if isz(deref(x))
                  then 0
                  else begin
                    setref(x, -(deref(x), 1));
                    (even 888)
                  end
        in begin setref(x, 13) ; (odd 888) end
    """
    runtest(input, None)

