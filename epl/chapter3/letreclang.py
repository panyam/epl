
import typing
from epl.unions import *
from epl.chapter3 import proclang

class LetRecExpr(object):
    """ To enable recursive procedures of the form:

        letrec F(x,y,z) = expression in expression
    """
    class Proc(object):
        def __init__(self, name, varnames, body):
            self.name = name
            self.varnames = varnames
            self.body = body

    def __init__(self, proc_map, body):
        """ proc_map ::  : typing.Dict[str, (typing.List[str], "Expr")] """
        self.procs = {k: LetRecExpr.Proc(k, v[0], v[1]) for k,v in proc_map.items()}
        self.body = body

class Expr(proclang.Expr):
    letrec = Variant(LetRecExpr)

class Eval(proclang.Eval):
    __caseon__ = Expr

    @case("letrec")
    def valueOfLetRec(self, procexpr, env):
        # Create a Procedure value that captures the proc expression as well as the current environment!
        return procexpr, env

