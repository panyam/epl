
from ipdb import set_trace
def eprint(expr):
    """ Pretty prints an expression. """
    val = expr.variant_value
    level, printable = val.printables()
    eprint_helper(level, printable)

def eprint_helper(level, printable):
    set_trace()
