
from ipdb import set_trace
from lark import Lark, Transformer

reserved_words = ["set", "letrec", "ref", "setref", "newref", "deref", "begin", "end", "let", "proc", "if", "isz"]

parser = Lark("""
        start : call_expr

        expr:   if_expr
            |   proc_expr
            |   let_expr
            |   letrec_expr
            |   paren_expr
            |   num
            |   var_expr
            |   tuple_expr
            |   iszero_expr
            |   block_expr
            |   ref_expr
            |   op_expr
            |   lazy_expr

        !num : NUMBER | "-" NUMBER

        lazy_expr : "'" call_expr

        block_expr : "begin" call_expr ( ";" call_expr ) * "end"
        ref_expr : refvar_expr | newref_expr | setref_expr | deref_expr | assign_expr
        refvar_expr : "ref" VARNAME
        newref_expr : "newref" "(" call_expr ")"
        deref_expr : "deref" "(" call_expr ")"
        setref_expr : "setref" "(" call_expr "," call_expr ")"

        assign_expr : "set" VARNAME "=" expr

        iszero_expr : "isz" call_expr 

        op_expr : OPERATOR call_expr

        var_expr : VARNAME

        varnames : VARNAME ( "," VARNAME ) *
        
        tuple_expr : "(" expr ( "," expr ) + ")"

        paren_expr : "(" call_expr ")"

        if_expr : "if" call_expr "then" call_expr "else" call_expr

        proc_expr : "proc" "(" varnames ")" call_expr

        let_expr : "let" let_mappings "in" call_expr
        let_mapping : VARNAME "=" call_expr
        let_mappings : let_mapping +
        
        letrec_expr : "letrec" letrec_mappings "in" call_expr
        letrec_mapping : VARNAME "(" varnames ")" "=" call_expr
        letrec_mappings : letrec_mapping +

        call_expr : expr | call_expr expr

        NUMBER : /[0-9]+/
        
        // VARNAME : /[a-zA-Z]+/
        VARNAME : /(?!{reserved_words})[_a-zA-Z][_a-zA-Z0-9]*/
        // OPERATOR : ( "*" "-" "^" "/" "+" ">" "<" "$" "&" "?" )+
        // OPERATOR : /[*-^/+\\>\\<$&?]+/
        OPERATOR : ( "*" | "-" | "^" | "/" | "+" | ">" | "<" | "$" | "&" | "?" )+
        %import common.WS
        %ignore WS
    """.format(reserved_words = "|".join(reserved_words)))

class BasicMixin(object):
    ### Call/Application expression
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
                    set_trace()
                    assert False
                params = mc[i + 1:i + count + 1]
                del mc[i + 1:i + count + 1]
                mc[i] = maker(params, self.expr_class)

        op,params = mc[0], mc[1:]
        if not params:
            return op
        return self.expr_class.as_call(op, *params)

    def expr(self, matches):
        self.assertIsExpr(matches, 1)
        return matches[0]

    def num(self, matches):
        mult = 1
        if len(matches) > 1:
            mult = -1
        token = matches[-1]
        assert token.type == 'NUMBER'
        return self.expr_class.as_num(int(token.value) * mult)

    def var_expr(self, matches):
        token = matches[0]
        assert len(matches) == 1 and token.type == 'VARNAME'
        out = self.expr_class.as_var(matches[0].value)
        return out
    
    def paren_expr(self, matches):
        self.assertIsExpr(matches, 1)
        return matches[0]

    def tuple_expr(self, matches):
        self.assertIsExpr(matches, -1)
        return self.expr_class.as_tup(*matches)

    def if_expr(self, matches):
        self.assertIsExpr(matches, 3)
        return self.expr_class.as_if(*matches)

    def lazy_expr(self, matches):
        self.assertIsExpr(matches)
        return self.expr_class.as_lazy(*matches)

class ExtMixin(object):
    def iszero_expr(self, matches):
        return self.expr_class.as_iszero(matches[0])

    def op_expr(self, matches):
        if matches[1].is_tup:
            tupexpr = matches[1].tupexpr
            return self.expr_class.as_opexpr(matches[0].value, tupexpr.children)
        else:
            return self.expr_class.as_opexpr(matches[0].value, matches[1])

class ProcMixin(object):
    def proc_expr(self, matches):
        varnames = [x.value for x in matches[0].children]
        return self.expr_class.as_proc(varnames, matches[1])

class LetMixin(object):
    def let_expr(self, matches):
        mappings = matches[0]
        body = matches[1]
        return self.expr_class.as_let(mappings, body)

    def let_mappings(self, matches):
        return dict(matches)

    def let_mapping(self, matches):
        return matches[0].value, matches[1]

class LetRecMixin(object):
    def letrec_expr(self, matches):
        mappings = matches[0]
        body = matches[1]
        return self.expr_class.as_letrec(mappings, body)

    def letrec_mappings(self, matches):
        return dict(matches)

    def letrec_mapping(self, matches):
        return (matches[0].value,
                self.expr_class.as_proc(
                    matches[1].children, matches[2]).procexpr)

class RefMixin(object):
    def block_expr(self, matches):
        self.assertIsExpr(matches)
        return self.expr_class.as_block(matches)

    def ref_expr(self, matches):
        self.assertIsExpr(matches)
        return matches[0]

    def refvar_expr(self, matches):
        return self.expr_class.as_ref(matches[0].value)

    def newref_expr(self, matches):
        self.assertIsExpr(matches)
        return self.expr_class.as_ref(matches[0])

    def deref_expr(self, matches):
        self.assertIsExpr(matches)
        return self.expr_class.as_deref(matches[0])

    def setref_expr(self, matches):
        self.assertIsExpr(matches)
        return self.expr_class.as_setref(matches[0], matches[1])

    def assign_expr(self, matches):
        return self.expr_class.as_assign(matches[0].value, matches[1])

class ASTTransformer(Transformer, BasicMixin, LetMixin, ProcMixin, LetRecMixin, ExtMixin, RefMixin):
    def __init__(self,expr_class, optable):
        self.expr_class = expr_class
        self.optable = optable

    def isExp(self, e):
        return type(e) is self.expr_class

    def assertIsExpr(self, matches, count = -1):
        try:
            assert count < 0 or len(matches) == count, "Expected %d exprs" % count
            assert all(map(self.isExp, matches))
        except Exception as e:
            set_trace()
            raise e

    def start(self, matches):
        self.assertIsExpr(matches, 1)
        return matches[0]

def parse(input, expr_class, optable = None, debug = False):
    optable = optable or {}
    tree = parser.parse(input)
    if debug:
        set_trace()
    return ASTTransformer(expr_class, optable).transform(tree), tree
