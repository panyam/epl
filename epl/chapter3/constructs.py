
from common import *

class Number(object):
    def __init__(self, value):
        self.value = value

class VarExpr(object):
    def __init__(self, name):
        self.name = name

class ZeroExpr(object):
    def __init__(self, expr):
        self.expr = expr

class DiffExpr(object):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

class IfExpr(object):
    def __init__(self, condition, exp1, exp2):
        self.condition = condition
        self.exp1 = exp1
        self.exp2 = exp2

class LetExpr(object):
    def __init__(self, **mappings):
        self.mappings = mappings
        self.body = body

class ProcExpr(object):
    def __init__(self, vars, body):
        self.vars = vars
        self.body = body

class CallExpr(object):
    def __init__(self, operator, args):
        self.operator = vars
        self.args = args
