
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
            |   op_expr

        !num : NUMBER | "-" NUMBER

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
        VARNAME : /(?!let|proc|if)[a-zA-Z]+/
        // OPERATOR : ( "*" "-" "^" "/" "+" ">" "<" "$" "&" "?" )+
        // OPERATOR : /[*-^/+\\>\\<$&?]+/
        OPERATOR : ( "*" | "-" | "^" | "/" | "+" | ">" | "<" | "$" | "&" | "?" )+
        %import common.WS
        %ignore WS
    """)

class ASTTransformer(Transformer):
    def __init__(self,expr_class, optable):
        self.expr_class = expr_class
        self.optable = optable

    def isExp(self, e):
        return type(e) is self.expr_class

    def assertIsExpr(self, matches, count = 1):
        try:
            assert count < 0 or len(matches) == count, "Expected %d exprs" % count
            assert all(map(self.isExp, matches))
        except Exception as e:
            set_trace()
            raise e

    def start(self, matches):
        self.assertIsExpr(matches)
        return matches[0]

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

    def proc_expr(self, matches):
        varnames = [x.value for x in matches[0].children]
        return self.expr_class.as_proc(varnames, matches[1])

    def if_expr(self, matches):
        self.assertIsExpr(matches, 3)
        return self.expr_class.as_if(*matches)

    ### Let patterns
    def let_expr(self, matches):
        mappings = matches[0]
        body = matches[1]
        return self.expr_class.as_let(mappings, body)

    def let_mappings(self, matches):
        return dict(matches)

    def let_mapping(self, matches):
        return matches[0].value, matches[1]

    ### Letrec patterns
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

def parse(input, expr_class, optable, debug = False):
    tree = parser.parse(input)
    if debug:
        set_trace()
    return ASTTransformer(expr_class, optable).transform(tree), tree
