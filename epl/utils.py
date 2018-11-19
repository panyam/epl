
from ipdb import set_trace

def indent(level): return "  " * level

def eprint(expr):
    """ Pretty prints an expression. """
    val = expr.variant_value 
    eprint_helper(val.printables())

def eprint_helper(printables, depth = 0):
    for level, printable in printables:
        if type(printable) is str:
            print(indent(depth + level) + printable)
        else:
            eprint_helper(printable, depth + level)
