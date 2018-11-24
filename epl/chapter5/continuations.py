

import typing
from epl.unions import *
from epl.chapter3 import letlang
from epl.chapter4 import lazylang

class Eval(CaseMatcher):
    __caseon__ = lazylang.Expr

    def applyContinuation(self, cont, expr):
        pass

    def valueOf(self, expr, env, cont = None):
        if cont is None:
            # Create end continuation
            cont = EndCont()
        return self(expr, env, cont)

    @case("lit")
    def valueOfLit(self, lit, env, cont):
        return cont.apply(self, lit)

    @case("var")
    def valueOfVar(self, var, env, cont):
        value = env.get(var.name)
        return cont.apply(self, value)

    @case("procexpr")
    def valueOfProcExpr(self, procexpr, env, cont):
        return cont.apply(self, procexpr.bind(env))

    @case("iszero")
    def valueOfIsZero(self, iszero, env, cont):
        return self.valueOf(iszero.expr, env, IsZeroCont(cont))

    @case("ifexpr")
    def valueOfIf(self, ifexpr, env, cont):
        # Eval mappings with end continuations
        nextcont = IfCont(ifexpr, env, cont)
        return nextcont.start(self)

    @case("let")
    def valueOfLet(self, let, env, cont):
        # With let we want to chain the let bindings one after the other
        # Eval mappings with end continuations
        nextcont = LetCont(let, env, cont)
        return nextcont.start(self)

    @case("letrec")
    def valueOfLetRec(self, letrec, env, cont):
        newenv = env.push()
        for proc in letrec.procs.values():
            newenv.setone(proc.name, proc.bind(newenv))
        return self.valueOf(letrec.body, newenv, cont)

    @case("tupexpr")
    def valueOfTupExpr(self, tupexpr, env, cont):
        nextcont = ExprListCont(tupexpr.children, env, cont,
                                self.__caseon__.as_tup)
        return nextcont.start(self)

    @case("opexpr")
    def valueOfOpExpr(self, opexpr, env, cont):
        # With let we want to chain the let bindings one after the other
        # Eval mappings with end continuations
        opfunc = env.get(opexpr.op)
        assert opfunc is not None, "No plug in found for operator: %s" % opexpr.op
        nextcont = ExprListCont(opexpr.exprs, env, cont, opfunc)
        return nextcont.start(self)

    @case("ref")
    def valueOfRef(self, ref, env, cont):
        if not ref.is_var:
            ref = self.__caseon__.as_ref(self.valueOf(ref.expr, env)).ref
        return cont.apply(self, ref)

    @case("deref")
    def valueOfDeRef(self, deref, env, cont):
        return self.valueOf(deref.expr, env, DeRefCont(env, cont))

    @case("setref")
    def valueOfSetRef(self, setref, env, cont):
        return self.valueOf(setref.ref, env, SetRefCont(setref, env, cont))

    @case("block")
    def valueOfBlock(self, block, env, cont):
        nextcont = ExprListCont(block.exprs, env, cont,
                            lambda results: results[-1])
        return nextcont.start(self)

    @case("assign")
    def valueOfAssign(self, assign, env, cont):
        return self.valueOf(assign.expr, env,
                    AssignCont(assign.varname, env, cont))

    @case("lazy")
    def valueOfLazy(self, lazy_expr, env, cont):
        return cont.apply(self, lazy_expr.bind(env))

    @case("thunk")
    def valueOfThunk(self, thunk, env, cont):
        return self.valueOf(thunk.expr, env, cont)

    @case("callexpr")
    def valueOfCall(self, callexpr, env, cont):
        nextcont = CallCont(callexpr, env, cont)
        return nextcont.start(self)

class Cont(object):
    def apply(self, Eval, expr) -> "Cont":
        assert False, "Implement this."

class EndCont(Cont):
    def apply(self, Eval, value : int) -> Cont:
        assert type(value) is letlang.Lit
        return value

class IsZeroCont(Cont):
    def __init__(self, cont):
        self.cont = cont

    def apply(self, Eval, value : int):
        return self.cont.apply(Eval, value == 0)

class IfCont(Cont):
    def __init__(self, ifexpr, env, cont):
        self.ifexpr = ifexpr
        self.env = env
        self.cont = cont

    def start(self, Eval):
        return Eval(self.ifexpr.cond, self.env, self)

    def apply(self, Eval, expr):
        if expr:
            return Eval(self.ifexpr.exp1, self.env, self.cont)
        else:
            return Eval(self.ifexpr.exp2, self.env, self.cont)

class ExprListCont(Cont):
    """ A general continuation that needs to evaluate and "collect" N expressions in before another operation that depends on these results can be performed.  Also it is required that we chain results from one to another."""
    def __init__(self, exprs, env, cont, onresults = None):
        self.curr = 0
        self.exprs = exprs
        self.env = env
        self.cont = cont
        self.onresults = onresults
        self.results = []

    def start(self, Eval):
        return Eval(self.exprs[0], self.env, self)

    def apply(self, Eval, expr):
        self.curr += 1
        self.results.append(expr)
        if self.curr < len(self.exprs):
            # we have more
            nextexpr = self.exprs[self.curr]
            return Eval(nextexpr, self.env, self)
        else:
            result = self.results
            if self.onresults:
                result = self.onresults(result)
            return self.cont.apply(Eval, result)

class DeRefCont(Cont):
    def __init__(self, env, cont):
        self.env = env
        self.cont = cont

    def apply(self, Eval, ref):
        result = ref.expr
        if ref.is_var:
            # Then get the value of the named ref
            result = self.env.get(ref.expr)
        return self.cont.apply(Eval, result)

class SetRefCont(Cont):
    def __init__(self, setref, env, cont):
        self.state = 0      # 0 = processing ref
                            # 1 == processing value
        self.setref = setref
        self.env = env
        self.cont = cont
        # results of setref child evaluations
        self.val1 = None

    def apply(self, Eval, ref):
        if self.state == 0:
            self.state += 1
            self.val1 = ref
            return Eval(self.setref.value, self.env, self)
        else:
            val2 = ref
            if self.val1.is_var:
                # since a named ref get the ref by name first - 
                # we have an extra level of indirection here
                self.env.replace(self.val1.expr, val2)
            else:
                # Set ref as is
                self.val1.expr = val2
            return self.cont.apply(Eval, val2)

class AssignCont(Cont):
    def __init__(self, varname, env, cont):
        self.varname = varname
        self.env = env
        self.cont = cont
    
    def apply(self, Eval, result):
        self.env.replace(self.varname, result)
        return self.cont.apply(Eval, result)

class LetCont(Cont):
    def __init__(self, letexpr, env, cont):
        self.curr = 0
        self.letexpr = letexpr
        self.varnames = list(letexpr.mappings.keys())
        self.env = env
        self.newenv = env.push()
        self.cont = cont

    def start(self, Eval):
        self.currvar = self.varnames[0]
        expr1 = self.letexpr.mappings[self.currvar]
        return Eval(expr1, self.env, self)

    def apply(self, Eval, expr):
        # Here we are called with the "expr" of the ith var being processed
        lastvar = self.currvar
        self.newenv.setone(lastvar, expr)
        self.curr += 1
        if self.curr < len(self.varnames):
            # Now evaluate the next var as if it is the body
            self.currvar = self.varnames[self.curr]
            nextexpr = self.letexpr.mappings[self.currvar]
            return Eval(nextpexr, self.newenv, self)
        else:
            # Here all bindings have been evaluated
            return Eval(self.letexpr.body, self.newenv, self.cont)

class CallCont(Cont):
    def __init__(self, callexpr, env, cont):
        self.callexpr = callexpr
        self.env = env
        self.cont = cont

    def start(self, Eval):
        return Eval(self.callexpr.operator, self.env, self)

    def apply(self, Eval, boundproc):
        # We just received operator result
        # so kick off arg 
        proc_cont = ApplyProcCont(boundproc, self.env, self.cont)
        nextcont = ExprListCont(self.callexpr.args, self.env, proc_cont)
        return nextcont.start(Eval)

class ApplyProcCont(Cont):
    def __init__(self, boundproc, env, cont):
        self.boundproc = boundproc
        self.env = env
        self.cont = cont

    def apply(self, Eval, args):
        # At this point operator and operands have been evaluated
        # So we need to do the "call" continuation
        # so each result is one "application"
        oldargs = currargs = args
        boundproc = self.boundproc
        procexpr, saved_env = boundproc.procexpr, boundproc.env
        if not currargs or not procexpr.varnames:
            assert False, "Called entry is *not* a function"

        nargs = len(procexpr.varnames)
        arglen = len(currargs)

        currargs,rest_args = currargs[:nargs], currargs[nargs:]
        newargs = dict(zip(procexpr.varnames, currargs))
        newenv = saved_env.extend(**newargs)

        if nargs > arglen:  # Time to curry
            left_varnames = procexpr.varnames[arglen:]
            newprocexpr = Eval.__caseon__.as_proc(left_varnames, procexpr.body).procexpr
            return self.cont.apply(Eval, newprocexpr.bind(newenv))

        elif nargs == arglen:
            return Eval(procexpr.body, newenv, self.cont)
        
        else: # nargs < arglen
            # Only take what we need and return rest as a call expr
            return Eval(procexpr, newenv, self.cont)
