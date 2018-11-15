
import typing
from epl.unions import *
from epl.chapter3 import proclang

class NamedProcExpr(proclang.ProcExpr):
    def __init__(self, name, varnames, body):
        proclang.ProcExpr.__init__(self, varnames, body)
        self.name = name

class LetRecExpr(object):
    """ To enable recursive procedures of the form:

        letrec F(x,y,z) = expression in expression
    """
    def __init__(self, proc_map, body):
        """ proc_map ::  : typing.Dict[str, (typing.List[str], "Expr")] """
        self.procs = {k: NamedProcExpr(k, v[0], v[1]) for k,v in proc_map.items()}
        self.body = body

class Expr(proclang.Expr):
    letrec = Variant(LetRecExpr)

class Eval(proclang.Eval):
    __caseon__ = Expr

    @case("letrec")
    def valueOfLetRec(self, letrec, env):
        # Create a Procedure value that captures the proc expression as well as the current environment!

        # New env returns a BoundProc if var in letrec.boundvars
        newenv = env.push()
        for proc in letrec.procs.values():
            newenv.setone(proc.name, proclang.BoundProc(proc, newenv))
        return self.valueOf(letrec.body, newenv)

