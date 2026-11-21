"""
NOMOS Equation Complexity Measures (Kolmogorov Proxy)
Agent E07
"""

import sympy as sp


def compute_equation_complexity(expr: sp.Expr) -> float:
    """
    Compute complexity score for SymPy expression:
    Counts number of leaf symbols, binary operations, function applications, and tree depth.
    Score = total_nodes + 0.5 * tree_depth
    """
    if expr == 0 or expr == sp.Integer(0):
        return 0.0

    node_count = sp.count_ops(expr) + len(expr.free_symbols) + 1

    # Estimate depth
    def get_depth(node):
        if not node.args:
            return 1
        return 1 + max(get_depth(arg) for arg in node.args)

    depth = get_depth(expr)
    return float(node_count + 0.5 * depth)
