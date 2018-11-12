

from epl.unions import *
from epl.chapter3.constructs import *
from epl.chapter3 import letlang

class Expr(letlang.Expr):
    procexpr = Variant(ProcExpr, checker = "is_proc", constructor = "as_proc")
    callexpr = Variant(CallExpr, checker = "is_call", constructor = "as_call")

class Eval(letlang.Eval):
    __caseon__ = Expr

    @case("procexpr")
    def valueOfProc(self, procexpr, env):
        # Create a Procedure value that captures the proc expression as well as the current environment!
        return procexpr, env

    @case("callexpr")
    def valueOfCall(self, callexpr, env):
        proc = self.valueOf(callexpr.operator, env)
        args = [self.valueOf(arg, env) for arg in callexpr.args]
        return self.apply_proc(proc, args)

    def apply_proc(self, proc, args):
        procexpr, saved_env = proc
        assert len(procexpr.varnames) == len(args), "Currying not supported for now :)"
        newargs = dict(zip(procexpr.varnames, args))
        newenv = saved_env.extend(**newargs)
        return self.valueOf(procexpr.body, newenv)

