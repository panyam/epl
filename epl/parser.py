
from ipdb import set_trace
from lark import Lark, Transformer

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
            |   diff_expr
            |   block_expr
            |   ref_expr
            |   op_expr

        !num : NUMBER | "-" NUMBER

        block_expr : "begin" call_expr ( ";" call_expr ) * "end"
        ref_expr : newref_expr | setref_expr | deref_expr | assign_expr
        newref_expr : "newref" "(" call_expr ")"
        deref_expr : "deref" "(" call_expr ")"
        setref_expr : "setref" "(" call_expr "," call_expr ")"

        assign_expr : "set" VARNAME "=" expr

        iszero_expr : "isz" "(" call_expr ")"
        diff_expr : "-" "(" call_expr "," call_expr ")"

        op_expr : OPERATOR call_expr

        var_expr : VARNAME // | OPERATOR

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
        VARNAME : /(?!set|letrec|setref|newref|deref|begin|end|let|proc|if)[a-zA-Z]+/
        // OPERATOR : ( "*" "-" "^" "/" "+" ">" "<" "$" "&" "?" )+
        // OPERATOR : /[*-^/+\\>\\<$&?]+/
        OPERATOR : ( "*" | "-" | "^" | "/" | "+" | ">" | "<" | "$" | "&" | "?" )+
        %import common.WS
        %ignore WS
    """)

class BasicMixin(object):
    ### Call/Application expression
    def call_expr(self, matches):
        self.assertIsExpr(matches, -1)
        if len(matches) == 1:
            return matches[0]

        mc = matches[:]
        if mc[0].is_var and mc[0].var.name in ("if", "proc"):
            set_trace()
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
        assert len(matches) == 1 and token.type in ('VARNAME', 'OPERATOR')
        out = self.expr_class.as_var(matches[0].value)
        out.var.is_op = token.type == 'OPERATOR'
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

class ExtMixin(object):
    def iszero_expr(self, matches):
        return self.expr_class.as_iszero(matches[0])

    def diff_expr(self, matches):
        return self.expr_class.as_diff(matches[0], matches[1])

    def op_expr(self, matches):
        op, params = matches[0],matches[1:]
        self.assertIsExpr(params, -1)
        assert len(params) == 1
        if op.value in self.optable:
            if not params[0].is_tup:
                set_trace()
                assert params[0].is_tup
            count,maker = self.optable[op.value]
            # Ensure we have enough elems
            return maker(params, self.expr_class)
        else:
            var = self.expr_class.as_var(op.value)
            var.is_op = True
            return self.expr_class.as_call(var, *params)

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

    def newref_expr(self, matches):
        self.assertIsExpr(matches)
        return self.expr_class.as_newref(matches[0])

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

def parse(input, expr_class, optable, debug = False):
    tree = parser.parse(input)
    if debug:
        set_trace()
    return ASTTransformer(expr_class, optable).transform(tree), tree
