
from ipdb import set_trace
from lark import Lark, Transformer

parser = Lark("""
        start : call_expr

        call_expr : expr +

        expr:   if_expr
            |   proc_expr
            |   let_expr
            |   letrec_expr
            |   paren_expr
            |   number
            |   var_expr
            |   tuple_expr

        number : NUMBER

        var_expr : VARNAME | OPERATOR

        varnames : VARNAME | VARNAME ( "," VARNAME ) *
        
        tuple_expr : "(" expr ( "," expr ) + ")"

        paren_expr : "(" call_expr ")"

        if_expr : "if" call_expr "then" call_expr "else" call_expr

        proc_expr : "proc" "(" varnames ")" call_expr

        let_expr : "let" let_mappings "in" call_expr
        let_mapping : VARNAME "=" call_expr
        let_mappings : let_mapping +
        
        letrec_expr : "letrec" letrec_mappings "in" call_expr
        letrec_mapping : VARNAME "(" varnames ")" "=" call_expr "in" call_expr
        letrec_mappings : letrec_mapping +

        NUMBER : /[0-9]+/
        VARNAME : /[a-zA-Z]+/
        // OPERATOR : ( "*" "-" "^" "/" "+" ">" "<" "$" "&" "?" )+
        // OPERATOR : /[*-^/+\\>\\<$&?]+/
        OPERATOR : ( "*" | "-" | "^" | "/" | "+" | ">" | "<" | "$" | "&" | "?" )+
        %import common.WS
        %ignore WS
    """)

class ASTTransformer(Transformer):
    def __init__(self,expr_class):
        self.expr_class = expr_class

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
        op = matches[0]
        params = matches[1:]
        if params:
            return self.expr_class.as_call(op, *params)
        return op

    def expr(self, matches):
        self.assertIsExpr(matches, 1)
        return matches[0]

    def number(self, matches):
        token = matches[0]
        assert len(matches) == 1 and token.type == 'NUMBER'
        return self.expr_class.as_number(int(matches[0].value))

    def var_expr(self, matches):
        token = matches[0]
        assert len(matches) == 1 and token.type in ('VARNAME', 'OPERATOR')
        return self.expr_class.as_var(matches[0].value)
    
    def paren_expr(self, matches):
        self.assertIsExpr(matches, 1)
        return matches[0]

    def tuple_expr(self, matches):
        self.assertIsExpr(matches, -1)
        return self.expr_class.as_tup(*matches)

    def if_expr(self, matches):
        self.assertIsExpr(matches, 3)
        return self.expr_class.as_if(*matches)

def parse(input, expr_class):
    tree = parser.parse(input)
    return ASTTransformer(expr_class).transform(tree)
