

from epl.unions import *
from epl.chapter3 import letlang

## Constructs for Procedures 

class ProcExpr(object):
    def __init__(self, varnames, body):
        if type(varnames) is str: varnames = [varnames]
        self.varnames = varnames
        self.body = body

    def __repr__(self):
        return "<Proc(%s) { %s }" % (", ".self.varnames, repr(self.body))

class CallExpr(object):
    def __init__(self, operator, *args):
        self.operator = operator
        self.args = list(args)

    def __repr__(self):
        return "<Call (%s) in %s" % (self.operator, ", ".join(map(repr, self.args)))


class Expr(letlang.Expr):
    procexpr = Variant(ProcExpr, checker = "is_proc", constructor = "as_proc")
    callexpr = Variant(CallExpr, checker = "is_call", constructor = "as_call")

class BoundProc(object):
    """ A procedure bound to an environment. """
    def __init__(self, proc, env):
        self.procexpr = proc
        self.env = env

class Eval(letlang.Eval):
    __caseon__ = Expr

    @case("procexpr")
    def valueOfProc(self, procexpr, env):
        # Create a Procedure value that captures the proc expression as well as the current environment!
        return BoundProc(procexpr, env)

    @case("callexpr")
    def valueOfCall(self, callexpr, env):
        boundproc = self.valueOf(callexpr.operator, env)
        args = [self.valueOf(arg, env) for arg in callexpr.args]
        return self.apply_proc(boundproc, args)

    def apply_proc(self, boundproc, args):
        procexpr, saved_env = boundproc.procexpr, boundproc.env
        assert len(procexpr.varnames) == len(args), "Currying not supported for now :)"
        newargs = dict(zip(procexpr.varnames, args))
        newenv = saved_env.extend(**newargs)
        return self.valueOf(procexpr.body, newenv)

