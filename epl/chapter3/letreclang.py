
import typing
from epl.unions import *
from epl.chapter3 import proclang

def NamedProcExpr(name, varnames, body):
    out = proclang.ProcExpr(varnames, body)
    out.name = name
    return out

class LetRecExpr(object):
    """ To enable recursive procedures of the form:

        letrec F(x,y,z) = expression in expression
    """
    def __init__(self, procs : typing.Dict[(str, proclang.ProcExpr)], body):
        for name, proc in procs.items():
            assert proc.name in (None, name)
            proc.name = name
        self.procs = procs
        self.body = body

    def printables(self):
        yield 0, "LetRec:"
        for proc in self.procs:
            yield 2, "%s (%s) = " % (proc.name, ",".join(proc.varnames))
            yield 3, proc.body.printables()
        yield 1, "in:"
        yield 2, self.body.printables()

    def __eq__(self, another):
        return self.procs == another.procs and \
               self.body == another.body

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

