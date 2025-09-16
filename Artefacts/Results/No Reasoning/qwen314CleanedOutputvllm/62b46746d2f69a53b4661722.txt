def absorb(self, args):
    """
    Given an `args` sequence of expressions, return a new list of expression applying absorption.
    """
    result = []
    for expr in args:
        if isinstance(expr, list):
            result.extend(self.absorb(expr))
        else:
            result.append(expr)
    return result