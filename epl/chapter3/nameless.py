
import typing
from epl.unions import *
from epl.chapter3 import letlang
from epl.chapter3 import proclang
from epl.chapter3 import letreclang

class NVar(object):
    """ A nameless variable. """
    def __init__(self, depth, index, lr_bound = False):
        self.depth = depth
        self.index = index
        self.lr_bound = lr_bound

    def printables(self):
        yield 0, "NVar (%d,%d,LR=%s)" % (self.depth, self.index, str(self.lr_bound))

    def __repr__(self):
        return "<NVar(%d:%d)>" % (self.depth, self.index)

class NProcExpr(object):
    def __init__(self, body):
        self.body = body

    def printables(self):
        yield 0, "NProc:"
        yield 1, self.body.printables()

    def __repr__(self):
        return "<NProc{ %s }" % repr(self.body)

class NLetExpr(object):
    """ Nameless let expressions.  No more mappings from var -> expr.  Only the "expr" is left and will be referred by indexes. """
    def __init__(self, values, body):
        self.values = values
        self.body = body

    def printables(self):
        yield 0, "NLet:"
        for v in self.values:
            yield 3, v.printables()
        yield 1, "in:"
        yield 2, self.body.printables()

class NLetRecExpr(object):
    """ To enable recursive procedures of the form:

        letrec F(x,y,z) = expression in expression
    """
    def __init__(self, proc_map, body):
        """ proc_map ::  : typing.Dict[str, (typing.List[str], "Expr")] """
        self.procs = {k: ProcExpr(k, v[0], v[1]) for k,v in proc_map.items()}
        self.body = body

    def printables(self):
        yield 0, "NLetRec:"
        for proc in self.procs.values():
            yield 2, "%s (%s) = " % (proc.name, ",".join(proc.varnames))
            yield 3, proc.body.printables()
        yield 1, "in:"
        yield 2, self.body.printables()

    def printables(self):
        yield 0, "NLet:"
        for v in self.values:
            yield 3, v.printables()
        yield 1, "in:"
        yield 2, self.body.printables()

class NExpr(Union):
    num = Variant(letlang.Number)
    diff = Variant(letlang.DiffExpr)
    iszero = Variant(letlang.IsZeroExpr)
    tupexpr = Variant(letlang.TupleExpr, checker = "is_tup", constructor = "as_tup")
    ifexpr = Variant(letlang.IfExpr, checker = "is_if", constructor = "as_if")
    callexpr = Variant(proclang.CallExpr, checker = "is_call", constructor = "as_call")

    # Nameless versions
    nvar = Variant(NVar)
    nlet = Variant(NLetExpr, checker = "is_nlet", constructor = "as_nlet")
    nletrec = Variant(NLetRecExpr)
    nprocexpr = Variant(NProcExpr, checker = "is_nproc", constructor = "as_nproc")

class NamelessTranslator(CaseMatcher):
    """ Translates an expression with variables to a nameless one with depths (and indexes).  """
    __caseon__ = letreclang.Expr

    class StaticEnv(object):
        """ A static environment used in the translation of a named program to its nameless counterpart. """
        def __init__(self, parent = None):
            self.depth = 0 if not parent else parent.depth + 1
            self.nvars = []

        def push(self):
            return StaticEnv(self)

        def nvar_for(self, name):
            for vname,nvar in self.nvars:
                if vname == name:
                    return nvar
            return None

        def register(self, var):
            assert nvar_for(var.name) is None, "Var already exists in this scope.  Push first?"
            
            nvar = NVar(self.depth, len(self.nvars))
            self.nvars.append((var.name, nvar))
            return nvar

    @case("num")
    def valueOfNumber(self, num, senv):
        return num

    @case("diff")
    def valueOfDiff(self, diff, senv):
        exp1 = self(diff.exp1, senv)
        exp2 = self(diff.exp2, senv)
        return Expr.as_diff(exp1, exp2)

    @case("tupexpr")
    def valueOfTupExpr(self, diff, senv):
        values = [self(v,env) for v in tupexpr.children]
        return TupleExpr(*values)

    @case("iszero")
    def valueOfIsZero(self, iszero, senv):
        return Expr.as_iszero(self(iszero.expr, senv))

    @case("ifexpr")
    def valueOfIf(self, ifexpr, senv):
        return Expr.as_if(self(ifexpr.exp1, senv), self(ifexpr.exp2, senv), self(ifexpr.exp3, senv))

    @case("var")
    def valueOfVar(self, var, senv):
        return env.register(var.name)

    @case("let")
    def valueOfLet(self, let, senv):
        newvalues = [self(v,senv) for v in let.values]
        newargs = let.mappings.keys()
        newenv = senv.push()
        map(newenv.register, let.mappings.keys())
        newbody = self(let.body, newenv)
        return Expr.as_nlet(newvalues, newbody)

    @case("letrec")
    def valueOfLetRec(self, letrec, senv):
        set_trace()
        newvalues = [self(v,senv) for v in let.values]
        newargs = let.mappings.keys()
        newenv = senv.push()
        map(newenv.register, let.mappings.keys())
        newbody = self(let.body, newenv)
        return Expr.as_nlet(newvalues, newbody)

    @case("procexpr")
    def valueOfProc(self, procexpr, senv):
        newenv = env.push()
        map(newenv.register, procexpr.varnames)
        newbody = self(body, newenv)
        return Expr.as_nproc(newbody)

    @case("callexpr")
    def valueOfCall(self, callexpr, senv):
        newbody = self(body, senv)
        newargs = [self(arg, senv) for arg in callexpr.args]
        return Expr.as_call(newbody, *newargs)

class Eval(CaseMatcher):
    """ An evaluator on the nameless expressions. """
    __caseon__ = NExpr

    class NEnv(object):
        """ A nameless environment used for evaluations. """
        pass

    @case("num")
    def valueOfNumber(self, num, env):
        return num

    @case("diff")
    def valueOfDiff(self, diff, env):
        exp1 = self(diff.exp1, env)
        exp2 = self(diff.exp2, env)
        return self(exp1, env) - self(exp2, env)

    @case("tupexpr")
    def valueOfTupExpr(self, tupexpr, env):
        values = [self(v,env) for v in tupexpr.children]
        return TupleExpr(*values)

    @case("iszero")
    def valueOfIsZero(self, iszero, env):
        return self(iszero.expr, env) == 0

    @case("ifexpr")
    def valueOfIf(self, ifexpr, env):
        if self(ifexpr.cond, env):
            return self(ifexpr.exp1, env)
        else:
            return self(ifexpr.exp2, env)

    @case("nprocexpr")
    def valueOfProc(self, procexpr, env):
        return proclang.BoundProc(procexpr, env)

    @case("nvar")
    def valueOfNVar(self, nvar, env):
        return env.get(nvar)

    @case("callexpr")
    def valueOfCall(self, callexpr, env):
        boundproc = self(callexpr.operator, env)
        newargs = [self(arg, env) for arg in callexpr.args]
        return self.apply_proc(boundproc, args)

    def apply_proc(self, boundproc, args):
        procexpr, saved_env = boundproc.procexpr, boundproc.env
        newenv = saved_env.extend(args)
        return self(procexpr.body, newenv)

    @case("nlet")
    def valueOfLet(self, let, env):
        newvalues = [self(v,env) for v in let.values]
        newenv = env.extend(*newvalues)
        return self(let.body, newenv)

    @case("nletrec")
    def valueOfLetRec(self, letrec, senv):
        set_trace()
        newvalues = [self(v,senv) for v in let.values]
        newargs = let.mappings.keys()
        newenv = senv.push()
        map(newenv.register, let.mappings.keys())
        newbody = self(let.body, newenv)
        return Expr.as_nlet(newvalues, newbody)
