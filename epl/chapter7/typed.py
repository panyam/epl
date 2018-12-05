
import typing
from epl import bp
from taggedunion import *
from epl.chapter5 import trylang
from epl.chapter5 import continuations

class TypeError(Exception):
    def __init__(self, expected, found):
        Exception.__init__(self, "Expected type: %s, Found: %s" % (expected, type))
        self.expected = expected
        self.found = found

def ensure_type(expected, found):
    if expected != found:
        raise TypeError(expected, found)

class BoxedType(object):
    def __init__(self, name, thetype):
        self.name = name
        self.thetype = thetype

    def __eq__(self, another):
        return self.name == another.name and self.thetype == another.thetype

    def __hash__(self):
        return hash((self.name, self.thetype))

class UnionType(object):
    def __init__(self, options):
        self.options = frozenset(options)

    def add(self, anothertype):
        if anothertype in self.options:
            return self
        return UnionType(self.options.union(set((anothertype,))))

    def __eq__(self, another):
        return self.options == another.options

    def __hash__(self):
        return hash(self.options)

class TupleType(object):
    def __init__(self, children):
        self.children = tuple(children)

    def __eq__(self, another):
        return self.children == another.children

    def __hash__(self):
        return hash(self.children)

class FuncType(object):
    def __init__(self, argtypes, rettype):
        self.argtypes = argtypes
        self.rettype = rettype

    def __eq__(self, another):
        return self.argtypes == another.argtypes and \
                self.rettype == another.rettype

    def __hash__(self):
        return hash(tuple(self.argtypes + (self.rettype,)))

class Type(Union):
    leaf = Variant(str)
    tup = Variant(TupleType)
    func = Variant(FuncType)
    box = Variant(BoxedType)

    def __hash__(self):
        return hash(self.variant_value)

class TypeOf(CaseMatcher):
    __caseon__ = trylang.Expr

    @case("lit")
    def typeOfLit(self, lit, tenv):
        return Type.as_leaf(type(lit.value).__name__)

    @case("var")
    def typeOfVar(self, var, tenv):
        return tenv.get(var.name)

    @case("tup")
    def typeOfTupExpr(self, tup, tenv):
        childtypes = [self(t, tenv) for t in tup.children]
        return Type.as_tup(childtypes)

    @case("iszero")
    def typeOfIsZero(self, iszero, tenv):
        t = self(iszero.expr, tenv)
        assert t.is_leaf and t.leaf == "int"
        return Type.as_leaf("bool")

    @case("opexpr")
    def typeOfOpExpr(self, opexpr, tenv):
        # For now assume opexpr takes all children of the same type so return type is same as child type
        argtypes = [self(a, tenv) for a in opexpr.arguments]
        assert all(a.is_leaf for a in argtypes)
        return argtypes[0]

    @case("ifexpr")
    def typeOfIfExpr(self, ifexpr, tenv):
        # For now assume opexpr takes all children of the same type so return type is same as child type
        condtype = self(ifexpr.cond, tenv)
        ensure_type(condtype, Type.as_leaf('bool'))
        exp1type = self(ifexpr.expr1, tenv)
        exp2type = self(ifexpr.expr1, tenv)
        assert exp1type == exp2type
        return exp2type

    @case("let")
    def typeOfLet(self, let, tenv):
        vartypes = {k: self(v, tenv) for k,v in let.mappings.items()}
        newenv = tenv.extend(**vartypes)
        bodytype = self(let.body, newenv)
        return bodytype

    @case("letrec")
    def typeOfLetRec(self, letrec, tenv):
        newenv = tenv.push()
        for proc in letrec.procs.values():
            newenv.setone(proc.name, Type.as_func(proc.argtypes, proc.rettype))
        body = letrec.body
        bodytype = self(body, newenv)
        return bodytype

    @case("procexpr")
    def typeOfProcExpr(self, procexpr, tenv):
        return Type.as_func(procexpr.argtypes, procexpr.rettype)

    @case("block")
    def typeOfBlock(self, block, tenv):
        result = None
        for e in block.exprs:
            result = self(e, tenv)
        return Type.as_leaf("void")

    @case("assign")
    def typeOfAssign(self, assign, tenv):
        vartype = tenv.get(assign.varname)
        valtype = self(assign.expr, tenv)
        assert vartype == valtype
        return vartype

    @case("ref")
    def typeOfRef(self, ref, tenv):
        thetype = self(ref.expr, tenv)
        return Type.as_box("ref", thetype)

    @case("setref")
    def typeOfSetRef(self, setref, tenv):
        reftype = self(setref.ref, tenv)
        assert reftype.name == "ref"
        valuetype = self(setref.value, tenv)
        assert reftype.thetype == valuetype
        return Type.as_leaf("void")

    @case("deref")
    def typeOfDeRef(self, deref, tenv):
        reftype = self(deref.ref, tenv)
        assert reftype.name == "ref"
        return reftype.thetype

    @case("lazy")
    def typeOfLazyExpr(self, lazy, tenv):
        thetype = self(lazy.expr, tenv)
        return Type.as_box("lazy", thetype)

    @case("thunk")
    def typeOfThunk(self, thunk, tenv):
        exptype = self(thunk.expr, tenv)
        assert exptype.is_box and exptype.box.name == "lazy"
        return exptype.box.thetype

    @case("callexpr")
    def typeOfCall(self, callexpr, tenv):
        optype = self(callexpr.operator, tenv)
        argtypes = [self(e, tenv) for e in callexpr.arguments]
        optype.func
        return optype.rettype

    @case("tryexpr")
    def typeOfTry(self, tryexpr, tenv):
        exptype = self(tryexpr.expr, tenv)
        handlertype = self(tryexpr.handler, tenv)
        ensure_type(exp_type, handlertype)
        return exptype

    @case("raiseexpr")
    def typeOfRaise(self, raiseexpr, tenv):
        exptype = self(raiseexpr.expr, tenv)
        return Type.as_box("exception", exptype)
