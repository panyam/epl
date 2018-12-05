
import functools
from epl import bp
from lark import Lark, Transformer

class Signature(object):
    argnames = []
    argtypes = []
    rettype = None

class BasicMixin(object):
    reserved = [ "if", "then", "else", "isz" ]
    reserved_ops = [ ]
    expr_rules = [ "num", "string", "var_expr", "tuple_expr", "iszero_expr", "op_expr", "paren_expr", "if_expr"  ]
    rules = [
        ("!num", """ SIGNED_NUMBER """),
        ("string",  """ STRING """),
        ("var_expr", """ VARNAME """ ),
        ("iszero_expr", """ "isz" call_expr  """),
        ("!op_expr", """ ( OPERATOR ) call_expr """ ),
        ("if_expr",  """ "if" call_expr "then" call_expr "else" call_expr """),
        ("tuple_expr", """ "(" call_expr ( "," call_expr ) + ")" """ ),
        ("paren_expr", """ "(" call_expr ")" """ ),
    ]

    def num(self, matches):
        mult = 1
        if len(matches) > 1:
            mult = -1
        token = matches[-1]
        assert token.type == 'SIGNED_NUMBER'
        return self.Expr.as_lit(int(token.value) * mult)

    def string(self, matches):
        strvalue = matches[0].value[1:-1]
        return self.Expr.as_lit(strvalue)

    def var_expr(self, matches):
        token = matches[0]
        assert len(matches) == 1 and token.type == 'VARNAME'
        out = self.Expr.as_var(matches[0].value)
        return out
    
    def paren_expr(self, matches):
        self.assertIsExpr(matches, 1)
        return matches[0]

    def tuple_expr(self, matches):
        self.assertIsExpr(matches, -1)
        return self.Expr.as_tup(*matches)

    def if_expr(self, matches):
        self.assertIsExpr(matches, 3)
        return self.Expr.as_if(*matches)

    def iszero_expr(self, matches):
        return self.Expr.as_iszero(matches[0])

    def op_expr(self, matches):
        if matches[1].is_tup:
            tup = matches[1].tup
            return self.Expr.as_opexpr(matches[0].value, tup.children)
        else:
            return self.Expr.as_opexpr(matches[0].value, matches[1])

class ProcMixin(object):
    reserved = [ "proc" ]
    reserved_ops = [ ]
    expr_rules = [ "proc_expr" ]
    rules = [
        ( "proc_expr", """ "proc" proc_signature call_expr """ ),
        ( "proc_signature", """ "(" param_decls ")" """ ),
        ( "param_decls", """ param_decl ( "," param_decl ) * """),
        ( "param_decl", """ VARNAME """)
    ]

    def proc_expr(self, matches):
        return self.create_procexpr(matches[0], matches[1])

    def proc_signature(self, matches):
        # Signature only has argnames
        assert len(matches) == 1
        param_decls = matches[0].children
        signature = Signature()
        signature.argnames = param_decls
        assert all([type(x) is str for x in signature.argnames])
        return signature

    def param_decl(self, matches):
        assert len(matches) == 1
        return matches[0].value

    def create_procexpr(self, signature, body):
        out = self.Expr.as_proc(signature.argnames, body)
        out.procexpr.argtypes = signature.argtypes
        out.procexpr.rettype = signature.rettype
        return out

class LetMixin(object):
    reserved = [ "let" ]
    reserved_ops = [ ]
    expr_rules = [ "let_expr" ]
    rules = [
        ( "let_expr", """ "let" let_mappings "in" call_expr """ ),
        ( "let_mapping", """ VARNAME "=" call_expr """ ),
        ( "let_mappings", """ let_mapping + """ ),
    ]

    def let_expr(self, matches):
        mappings = matches[0]
        body = matches[1]
        return self.Expr.as_let(mappings, body)

    def let_mappings(self, matches):
        return dict(matches)

    def let_mapping(self, matches):
        return matches[0].value, matches[1]

class LetRecMixin(object):
    reserved = [ "letrec" ]
    reserved_ops = [ ]
    expr_rules = [ "letrec_expr" ]
    rules = [
        ( "letrec_expr", """ "letrec" letrec_mappings "in" call_expr """ ),
        ( "letrec_mapping", """ VARNAME proc_signature "=" call_expr """ ),
        ( "letrec_mappings", """ letrec_mapping + """ ),
    ]
    def letrec_expr(self, matches):
        mappings = matches[0]
        body = matches[1]
        return self.Expr.as_letrec(mappings, body)

    def letrec_mappings(self, matches):
        return dict(matches)

    def letrec_mapping(self, matches):
        return (matches[0].value, self.create_procexpr(matches[1], matches[2]).procexpr)

class RefMixin(object):
    reserved = [ "set", "ref", "setref", "newref", "deref", "begin", "end" ]
    reserved_ops = [ ]
    expr_rules = [ "ref_expr", "block_expr", "proc_expr" ]
    rules = [
        ( "block_expr", """ "begin" call_expr ( ";" call_expr ) * "end" """ ),
        ( "ref_expr", """ refvar_expr | newref_expr | setref_expr | deref_expr | assign_expr """ ),
        ( "refvar_expr", """ "ref" VARNAME """ ),
        ( "newref_expr", """ "newref" "(" call_expr ")" """ ),
        ( "deref_expr", """ "deref" "(" call_expr ")" """ ),
        ( "setref_expr", """ "setref" "(" call_expr "," call_expr ")" """ ),
        ( "assign_expr", """ "set" VARNAME "=" expr """ )
    ]

    def block_expr(self, matches):
        self.assertIsExpr(matches)
        return self.Expr.as_block(matches)

    def ref_expr(self, matches):
        self.assertIsExpr(matches)
        return matches[0]

    def refvar_expr(self, matches):
        return self.Expr.as_ref(matches[0].value)

    def newref_expr(self, matches):
        self.assertIsExpr(matches)
        return self.Expr.as_ref(matches[0])

    def deref_expr(self, matches):
        self.assertIsExpr(matches)
        return self.Expr.as_deref(matches[0])

    def setref_expr(self, matches):
        self.assertIsExpr(matches)
        return self.Expr.as_setref(matches[0], matches[1])

    def assign_expr(self, matches):
        return self.Expr.as_assign(matches[0].value, matches[1])

class TryMixin(object):
    reserved = [ "try", "raise" ]
    reserved_ops = [ ]
    expr_rules = [ "try_expr", "raise_expr", "lazy_expr" ]
    rules = [
        ( "lazy_expr", """ "'" call_expr """ ),
        ( "try_expr", """ "try" call_expr "catch" "(" VARNAME ")" call_expr """ ),
        ( "raise_expr", """ "raise" call_expr """ )
    ]

    def lazy_expr(self, matches):
        self.assertIsExpr(matches)
        return self.Expr.as_lazy(*matches)

    def try_expr(self, matches):
        expr, varname, handlerexpr = matches
        return self.Expr.as_tryexpr(expr, varname, handlerexpr)

    def raise_expr(self, matches):
        return self.Expr.as_raiseexpr(matches[0])

class TypingMixin(object):
    reserved = []
    reserved_ops = [ "->" ]
    expr_rules = [ ]
    rules = [
        ( "proc_signature", """ "(" param_decls ")" ( "->" type_decl ) ? """ ),
        ( "param_decl", """ VARNAME ( ":" type_decl ) ? """),

        ( "type_decl", """ no_type_decl | basic_type_decl | tuple_type_decl | func_type_decl """ ),
        ( "no_type_decl", """ "?" """ ),
        ( "basic_type_decl", """ VARNAME """ ),
        ( "tuple_type_decl", """ "(" type_decl ( "," type_decl ) * ")" """ ),
        ( "func_type_decl", """ type_decl  ( "->" type_decl ) + """)
    ]

    def proc_signature(self, matches):
        assert len(matches) in (1, 2)
        param_decls = matches[0].children
        # Signature only has argnames
        signature = Signature()
        signature.argnames = [p[0] for p in param_decls]
        signature.argtypes = [p[1] for p in param_decls]
        if len(matches) == 2:
            signature.rettype = matches[1]
        if not all([type(x) is str for x in signature.argnames]): bp.debug()
        return signature

    def param_decl(self, matches):
        assert len(matches) in (1, 2)
        if len(matches) == 1:
            return matches[0].value, None
        else:
            return matches[0].value, matches[1]

    def type_decl(self, matches):
        assert len(matches) == 1
        return matches[0]

    def func_type_decl(self, matches):
        bp.debug()

    def no_type_decl(self, matches):
        assert len(matches) == 0
        bp.debug()
        return None

    def basic_type_decl(self, matches):
        assert len(matches) == 1
        assert matches[0].type == 'VARNAME'
        return self.Type.as_leaf(matches[0].value)

    def tuple_type_decl(self, matches):
        bp.debug()

class BaseTransformer(Transformer):
    def __init__(self,Expr, Type, optable):
        self.Expr = Expr
        self.Type = Type
        self.optable = optable

    def start(self, matches):
        self.assertIsExpr(matches, 1)
        return matches[0]

    def expr(self, matches):
        self.assertIsExpr(matches, 1)
        return matches[0]

    def call_expr(self, matches):
        self.assertIsExpr(matches, -1)
        if len(matches) == 1:
            return matches[0]

        mc = matches[:]
        # Start from reverse and keep folding operators
        # as they have a higher precedence
        # TODO - apply proper operator precedence where required
        for i in range(len(mc) - 1, -1, -1):
            m = mc[i]
            if m.is_var and m.var.name in self.optable:
                count,maker = self.optable[m.var.name]
                # Ensure we have enough elems
                if (len(mc) - i) < (count + 1):
                    bp.debug()
                    assert False
                params = mc[i + 1:i + count + 1]
                del mc[i + 1:i + count + 1]
                mc[i] = maker(params, self.Expr)

        op,params = mc[0], mc[1:]
        if not params:
            return op
        return self.Expr.as_call(op, *params)

    def isExp(self, e):
        return type(e) is self.Expr

    def assertIsExpr(self, matches, count = -1):
        try:
            assert count < 0 or len(matches) == count, "Expected %d exprs" % count
            assert all(map(self.isExp, matches))
        except Exception as e:
            bp.debug()
            raise e

def make_parser(Expr, Type, optable = None, *mixins):
    class Parser(object):
        def __init__(self):
            bases = tuple([BaseTransformer] + list(reversed(mixins)))
            self.transformer_class = type("ASTTransformer", bases, {})
            self.transformer = self.transformer_class(Expr, Type,
                                                      optable or {})

            expr_rules = functools.reduce(lambda x,y: x + y, [m.expr_rules for m in mixins], [])
            sub_rules = []
            for m in mixins:
                for nt,rule in m.rules:
                    for i,sr in enumerate(sub_rules):
                        if sr[0] == nt:
                            del sub_rules[i]
                            break
                    sub_rules.append((nt,rule))
            reserved_words = "|".join(functools.reduce(lambda x,y: x+y, [m.reserved for m in mixins], []))
            reserved_ops = "|".join(functools.reduce(lambda x,y: x+y, [m.reserved_ops for m in mixins], []))
            reserved_ops_regex = ""
            if reserved_ops:
                reserved_ops_regex = "(?!{reserved_ops})".format(reserved_ops = reserved_ops)
            indentstr = "    " * 4

            self.grammar = """
                start : call_expr

                call_expr : expr | call_expr expr

                expr: {expr_rules}

                \n{sub_rules}

                STRING:     /\\\"(\\\\.|[^"\\\\])*\\\"/
                VARNAME:    /(?!{reserved_words})[_a-zA-Z][_a-z\\-A-Z0-9]*/
                // OPCHAR :   ( "*" | "-" | "^" | "/" | "+" | ">" | "<" | "$" | "&" | "?" )
                // OPERATOR:   ( "*" | "-" | "^" | "/" | "+" | ">" | "<" | "$" | "&" | "?" )+
                OPERATOR:   /{reserved_ops_regex}[-\\/!$%^+&*?<>]+/

                %import common.SIGNED_NUMBER
                %import common.WS
                %ignore WS
            """.format(reserved_words = reserved_words, 
                        reserved_ops_regex = reserved_ops_regex,
                        sub_rules = "\n\n".join(("%s%s : %s" % (indentstr, m[0], m[1])) for m in sub_rules),
                        expr_rules = ("\n%s|    " % indentstr).join(expr_rules))
            bp.debug("debuggrammar")
            self.larkparser = Lark(self.grammar)

        def parse(self, input):
            tree = self.larkparser.parse(input)
            return self.transformer.transform(tree), tree
    return Parser()

