"""
NOMOS Spatiotemporal Differential Expression Grammar & AST Engine
Phase 6: Open-Ended Differential Expression Grammar
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import numpy as np
import sympy as sp

from nomos.pde.operators import compute_derivative


class DiffNodeType(Enum):
    # Terminals
    FIELD_VAR = auto()      # 'u', 'v', 'omega', etc.
    CONSTANT = auto()       # scalar c

    # Differential operators (spatial 1D & 2D)
    DIFF_X = auto()         # d/dx
    DIFF_XX = auto()        # d^2/dx^2
    DIFF_XXX = auto()       # d^3/dx^3
    DIFF_XXXX = auto()      # d^4/dx^4
    DIFF_Y = auto()         # d/dy
    DIFF_YY = auto()        # d^2/dy^2
    LAPLACIAN = auto()      # d^2/dx^2 + d^2/dy^2

    # Algebraic operations
    NEG = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    POW = auto()            # integer powers (e.g. u^2, u^3)


class DiffNode:
    """
    AST node for differential expressions over spatiotemporal fields.
    """

    def __init__(
        self,
        node_type: DiffNodeType,
        name: str = "",
        value: float = 0.0,
        children: Optional[List["DiffNode"]] = None,
    ):
        self.node_type = node_type
        self.name = name
        self.value = float(value)
        self.children = children or []

    @property
    def arity(self) -> int:
        return len(self.children)

    def is_terminal(self) -> bool:
        return len(self.children) == 0

    def copy(self) -> "DiffNode":
        return DiffNode(
            node_type=self.node_type,
            name=self.name,
            value=self.value,
            children=[c.copy() for c in self.children],
        )

    def count_nodes(self) -> int:
        return 1 + sum(c.count_nodes() for c in self.children)

    def depth(self) -> int:
        if self.is_terminal():
            return 1
        return 1 + max(c.depth() for c in self.children)

    def evaluate(
        self,
        u_dict: Dict[str, np.ndarray],
        dx: float,
        dy: float = 0.0,
        periodic: bool = True,
        method: str = "fd",
    ) -> np.ndarray:
        """
        Recursively evaluate differential expression on spatiotemporal grid.
        Input u_dict: {"u": U, ...} where U has shape (M, Nx) or (M, Nx, Ny).
        Output: field array matching grid shape.
        """
        nt = self.node_type

        # Terminals
        if nt == DiffNodeType.FIELD_VAR:
            if self.name in u_dict:
                return u_dict[self.name]
            return u_dict["u"]

        elif nt == DiffNodeType.CONSTANT:
            # Broadcast constant to grid shape
            ref = next(iter(u_dict.values()))
            return np.full_like(ref, self.value)

        # Differential operators
        elif nt == DiffNodeType.DIFF_X:
            child_val = self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)
            axis = 1 if child_val.ndim in (2, 3) else 0
            return compute_derivative(child_val, dx=dx, order=1, method=method, periodic=periodic, axis=axis)

        elif nt == DiffNodeType.DIFF_XX:
            child_val = self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)
            axis = 1 if child_val.ndim in (2, 3) else 0
            return compute_derivative(child_val, dx=dx, order=2, method=method, periodic=periodic, axis=axis)

        elif nt == DiffNodeType.DIFF_XXX:
            child_val = self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)
            axis = 1 if child_val.ndim in (2, 3) else 0
            return compute_derivative(child_val, dx=dx, order=3, method=method, periodic=periodic, axis=axis)

        elif nt == DiffNodeType.DIFF_XXXX:
            child_val = self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)
            axis = 1 if child_val.ndim in (2, 3) else 0
            return compute_derivative(child_val, dx=dx, order=4, method=method, periodic=periodic, axis=axis)

        elif nt == DiffNodeType.DIFF_Y:
            child_val = self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)
            axis = 2 if child_val.ndim == 3 else -1
            effective_dy = dy if dy > 0 else dx
            return compute_derivative(child_val, dx=effective_dy, order=1, method=method, periodic=periodic, axis=axis)

        elif nt == DiffNodeType.DIFF_YY:
            child_val = self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)
            axis = 2 if child_val.ndim == 3 else -1
            effective_dy = dy if dy > 0 else dx
            return compute_derivative(child_val, dx=effective_dy, order=2, method=method, periodic=periodic, axis=axis)

        elif nt == DiffNodeType.LAPLACIAN:
            child_val = self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)
            if child_val.ndim == 3:
                effective_dy = dy if dy > 0 else dx
                dxx = compute_derivative(child_val, dx=dx, order=2, method=method, periodic=periodic, axis=1)
                dyy = compute_derivative(child_val, dx=effective_dy, order=2, method=method, periodic=periodic, axis=2)
                return dxx + dyy
            else:
                return compute_derivative(child_val, dx=dx, order=2, method=method, periodic=periodic, axis=-1)

        # Algebraic operations
        elif nt == DiffNodeType.NEG:
            return -self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)

        elif nt == DiffNodeType.ADD:
            return self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method) + \
                   self.children[1].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)

        elif nt == DiffNodeType.SUB:
            return self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method) - \
                   self.children[1].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)

        elif nt == DiffNodeType.MUL:
            return self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method) * \
                   self.children[1].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)

        elif nt == DiffNodeType.POW:
            base = self.children[0].evaluate(u_dict, dx=dx, dy=dy, periodic=periodic, method=method)
            power = int(self.value) if self.value != 0 else 2
            return base**power

        raise NotImplementedError(f"Unsupported node type {nt}")

    def to_sympy(self) -> sp.Expr:
        """Convert differential AST to symbolic SymPy expression."""
        nt = self.node_type
        x_sym = sp.Symbol("x")
        y_sym = sp.Symbol("y")
        vname = self.name or "u"
        u_func = sp.Function(vname)(x_sym)

        if nt == DiffNodeType.FIELD_VAR:
            return u_func

        elif nt == DiffNodeType.CONSTANT:
            return sp.Float(self.value)

        elif nt == DiffNodeType.DIFF_X:
            return sp.Derivative(self.children[0].to_sympy(), x_sym, 1)

        elif nt == DiffNodeType.DIFF_XX:
            return sp.Derivative(self.children[0].to_sympy(), x_sym, 2)

        elif nt == DiffNodeType.DIFF_XXX:
            return sp.Derivative(self.children[0].to_sympy(), x_sym, 3)

        elif nt == DiffNodeType.DIFF_XXXX:
            return sp.Derivative(self.children[0].to_sympy(), x_sym, 4)

        elif nt == DiffNodeType.DIFF_Y:
            return sp.Derivative(self.children[0].to_sympy(), y_sym, 1)

        elif nt == DiffNodeType.DIFF_YY:
            return sp.Derivative(self.children[0].to_sympy(), y_sym, 2)

        elif nt == DiffNodeType.LAPLACIAN:
            child_sym = self.children[0].to_sympy()
            return sp.Derivative(child_sym, x_sym, 2) + sp.Derivative(child_sym, y_sym, 2)

        elif nt == DiffNodeType.NEG:
            return -self.children[0].to_sympy()

        elif nt == DiffNodeType.ADD:
            return self.children[0].to_sympy() + self.children[1].to_sympy()

        elif nt == DiffNodeType.SUB:
            return self.children[0].to_sympy() - self.children[1].to_sympy()

        elif nt == DiffNodeType.MUL:
            return self.children[0].to_sympy() * self.children[1].to_sympy()

        elif nt == DiffNodeType.POW:
            p = int(self.value) if self.value != 0 else 2
            return self.children[0].to_sympy() ** p

        return sp.Symbol("unknown")

    def to_string(self) -> str:
        """Human-readable mathematical string."""
        nt = self.node_type
        if nt == DiffNodeType.FIELD_VAR:
            return self.name or "u"
        elif nt == DiffNodeType.CONSTANT:
            return f"{self.value:.4f}"
        elif nt == DiffNodeType.DIFF_X:
            return f"Dx({self.children[0].to_string()})"
        elif nt == DiffNodeType.DIFF_XX:
            return f"Dxx({self.children[0].to_string()})"
        elif nt == DiffNodeType.DIFF_XXX:
            return f"Dxxx({self.children[0].to_string()})"
        elif nt == DiffNodeType.DIFF_XXXX:
            return f"Dxxxx({self.children[0].to_string()})"
        elif nt == DiffNodeType.DIFF_Y:
            return f"Dy({self.children[0].to_string()})"
        elif nt == DiffNodeType.DIFF_YY:
            return f"Dyy({self.children[0].to_string()})"
        elif nt == DiffNodeType.LAPLACIAN:
            return f"Laplacian({self.children[0].to_string()})"
        elif nt == DiffNodeType.NEG:
            return f"-({self.children[0].to_string()})"
        elif nt == DiffNodeType.ADD:
            return f"({self.children[0].to_string()} + {self.children[1].to_string()})"
        elif nt == DiffNodeType.SUB:
            return f"({self.children[0].to_string()} - {self.children[1].to_string()})"
        elif nt == DiffNodeType.MUL:
            return f"({self.children[0].to_string()} * {self.children[1].to_string()})"
        elif nt == DiffNodeType.POW:
            p = int(self.value) if self.value != 0 else 2
            return f"({self.children[0].to_string()}**{p})"
        return "unknown"


def check_differential_algebraic_equivalence(expr1_str: str, expr2_str: str) -> bool:
    """
    Check if two differential expressions are algebraically equivalent under SymPy differentiation rules.
    Example: d(u^2)/dx == 2*u*u_x, Laplacian(u) == u_xx + u_yy.
    """
    x = sp.Symbol("x")
    y = sp.Symbol("y")
    u = sp.Function("u")(x, y)
    v = sp.Function("v")(x, y)
    omega = sp.Function("omega")(x, y)

    u_x = sp.Derivative(u, x)
    u_xx = sp.Derivative(u, x, 2)
    u_xxx = sp.Derivative(u, x, 3)
    u_xxxx = sp.Derivative(u, x, 4)
    u_y = sp.Derivative(u, y)
    u_yy = sp.Derivative(u, y, 2)

    v_x = sp.Derivative(v, x)
    v_xx = sp.Derivative(v, x, 2)
    v_y = sp.Derivative(v, y)
    v_yy = sp.Derivative(v, y, 2)

    local_dict = {
        "x": x,
        "y": y,
        "u": u,
        "v": v,
        "omega": omega,
        "u_x": u_x,
        "u_xx": u_xx,
        "u_xxx": u_xxx,
        "u_xxxx": u_xxxx,
        "u_y": u_y,
        "u_yy": u_yy,
        "v_x": v_x,
        "v_xx": v_xx,
        "v_y": v_y,
        "v_yy": v_yy,
        "Dx": lambda arg: sp.Derivative(arg, x),
        "Dxx": lambda arg: sp.Derivative(arg, x, 2),
        "Dxxx": lambda arg: sp.Derivative(arg, x, 3),
        "Dxxxx": lambda arg: sp.Derivative(arg, x, 4),
        "Dy": lambda arg: sp.Derivative(arg, y),
        "Dyy": lambda arg: sp.Derivative(arg, y, 2),
        "Laplacian": lambda arg: sp.Derivative(arg, x, 2) + sp.Derivative(arg, y, 2),
    }

    try:
        e1 = sp.sympify(expr1_str, locals=local_dict)
        e2 = sp.sympify(expr2_str, locals=local_dict)

        diff = sp.simplify((e1 - e2).doit())
        return diff == 0
    except Exception:
        return False
