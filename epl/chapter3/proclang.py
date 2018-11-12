

from constructs import *
import letlang

class Expr(letlang.Expr):
    procexpr = Variant(ProcExpr)
    callexpr = Variant(CallExpr)

class Eval(letlang.Eval):
    __caseon__ = Expr

    @case("procexpr")
    def valueOfProc(self, procexpr, env):
        # Create a Procedure value that captures the proc expression as well as the current environment!
        return procexpr, env

    @case("callexpr")
    def valueOfCall(self, callexpr, env):
        proc,env = self.valueOf(callexpr.operator, env)
        args = [valueOf(arg, env) for arg in expr.callexpr.args]
        return self.apply_proc(proc, args)

    def apply_proc(self, proc, args):
        procexpr, saved_env = proc
        assert len(procexpr.vars) == len(args), "Currying not supported for now :)"
        newargs = dict(zip(procexpr.vars, args))
        newenv = saved_env.extend(**newargs)
        return valueOf(procexpr.body, newenv)

set_trace()
