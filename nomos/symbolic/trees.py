"""
NOMOS Typed Expression Tree AST & Evaluation Engine
Milestone M2 — Phase 2 Expression Representation
Agents D01, E01, E02, E07, E08, E09
"""

from dataclasses import dataclass, field
import json
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import sympy as sp

from nomos.symbolic.primitives import (
    NodeType,
    protected_div,
    protected_log,
    protected_exp,
    protected_sqrt,
    protected_pow,
)


class ExpressionNode:
    """
    Typed AST node for arbitrary nonlinear expression trees.
    Supports variables, constants, unary, and binary operators.
    """

    def __init__(
        self,
        node_type: NodeType,
        name: str = "",
        value: float = 0.0,
        children: Optional[List["ExpressionNode"]] = None,
        units: Optional[Dict[str, int]] = None,
    ):
        self.node_type = node_type
        self.name = name
        self.value = float(value)
        self.children = children or []
        self.units = units or {}

    @property
    def arity(self) -> int:
        return len(self.children)

    def is_terminal(self) -> bool:
        return len(self.children) == 0

    def copy(self) -> "ExpressionNode":
        return ExpressionNode(
            node_type=self.node_type,
            name=self.name,
            value=self.value,
            children=[c.copy() for c in self.children],
            units=dict(self.units),
        )

    def count_nodes(self) -> int:
        return 1 + sum(c.count_nodes() for c in self.children)

    def max_depth(self) -> int:
        if not self.children:
            return 1
        return 1 + max(c.max_depth() for c in self.children)

    def get_constants(self) -> List[float]:
        res = []
        if self.node_type == NodeType.CONSTANT:
            res.append(self.value)
        for c in self.children:
            res.extend(c.get_constants())
        return res

    def set_constants(self, values: List[float], idx: int = 0) -> int:
        if self.node_type == NodeType.CONSTANT:
            self.value = float(values[idx])
            idx += 1
        for c in self.children:
            idx = c.set_constants(values, idx)
        return idx

    def evaluate(self, var_map: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Evaluate expression tree vectorially on dictionary of state arrays.
        """
        if self.node_type == NodeType.VARIABLE or self.node_type == NodeType.CONTROL:
            if self.name not in var_map:
                raise KeyError(f"Variable '{self.name}' not found in state mapping: {list(var_map.keys())}")
            return var_map[self.name]

        elif self.node_type == NodeType.CONSTANT:
            # Broadcast constant to match shape of inputs
            sample_val = next(iter(var_map.values()))
            if isinstance(sample_val, np.ndarray):
                return np.full_like(sample_val, self.value, dtype=np.float64)
            return np.array([self.value], dtype=np.float64)

        elif self.node_type == NodeType.NEG:
            return -self.children[0].evaluate(var_map)

        elif self.node_type == NodeType.SIN:
            return np.sin(self.children[0].evaluate(var_map))

        elif self.node_type == NodeType.COS:
            return np.cos(self.children[0].evaluate(var_map))

        elif self.node_type == NodeType.EXP:
            return protected_exp(self.children[0].evaluate(var_map))

        elif self.node_type == NodeType.LOG:
            return protected_log(self.children[0].evaluate(var_map))

        elif self.node_type == NodeType.SQRT:
            return protected_sqrt(self.children[0].evaluate(var_map))

        elif self.node_type == NodeType.ABS:
            return np.abs(self.children[0].evaluate(var_map))

        elif self.node_type == NodeType.ADD:
            return self.children[0].evaluate(var_map) + self.children[1].evaluate(var_map)

        elif self.node_type == NodeType.SUB:
            return self.children[0].evaluate(var_map) - self.children[1].evaluate(var_map)

        elif self.node_type == NodeType.MUL:
            return self.children[0].evaluate(var_map) * self.children[1].evaluate(var_map)

        elif self.node_type == NodeType.DIV:
            return protected_div(
                self.children[0].evaluate(var_map),
                self.children[1].evaluate(var_map),
            )

        elif self.node_type == NodeType.POW:
            return protected_pow(
                self.children[0].evaluate(var_map),
                self.children[1].evaluate(var_map),
            )

        raise ValueError(f"Unknown NodeType: {self.node_type}")

    def to_sympy(self) -> sp.Expr:
        if self.node_type in (NodeType.VARIABLE, NodeType.CONTROL):
            return sp.Symbol(self.name)
        elif self.node_type == NodeType.CONSTANT:
            return sp.Float(round(self.value, 6))
        elif self.node_type == NodeType.NEG:
            return -self.children[0].to_sympy()
        elif self.node_type == NodeType.SIN:
            return sp.sin(self.children[0].to_sympy())
        elif self.node_type == NodeType.COS:
            return sp.cos(self.children[0].to_sympy())
        elif self.node_type == NodeType.EXP:
            return sp.exp(self.children[0].to_sympy())
        elif self.node_type == NodeType.LOG:
            return sp.log(sp.Abs(self.children[0].to_sympy()))
        elif self.node_type == NodeType.SQRT:
            return sp.sqrt(sp.Abs(self.children[0].to_sympy()))
        elif self.node_type == NodeType.ABS:
            return sp.Abs(self.children[0].to_sympy())
        elif self.node_type == NodeType.ADD:
            return self.children[0].to_sympy() + self.children[1].to_sympy()
        elif self.node_type == NodeType.SUB:
            return self.children[0].to_sympy() - self.children[1].to_sympy()
        elif self.node_type == NodeType.MUL:
            return self.children[0].to_sympy() * self.children[1].to_sympy()
        elif self.node_type == NodeType.DIV:
            denom = self.children[1].to_sympy()
            return self.children[0].to_sympy() / denom
        elif self.node_type == NodeType.POW:
            return self.children[0].to_sympy() ** self.children[1].to_sympy()
        raise ValueError(f"Unknown node type: {self.node_type}")

    def to_string(self) -> str:
        if self.node_type in (NodeType.VARIABLE, NodeType.CONTROL):
            return self.name
        elif self.node_type == NodeType.CONSTANT:
            return f"{self.value:.4g}"
        elif self.node_type == NodeType.NEG:
            return f"(-{self.children[0].to_string()})"
        elif self.node_type == NodeType.SIN:
            return f"sin({self.children[0].to_string()})"
        elif self.node_type == NodeType.COS:
            return f"cos({self.children[0].to_string()})"
        elif self.node_type == NodeType.EXP:
            return f"exp({self.children[0].to_string()})"
        elif self.node_type == NodeType.LOG:
            return f"log({self.children[0].to_string()})"
        elif self.node_type == NodeType.SQRT:
            return f"sqrt({self.children[0].to_string()})"
        elif self.node_type == NodeType.ABS:
            return f"abs({self.children[0].to_string()})"
        elif self.node_type == NodeType.ADD:
            return f"({self.children[0].to_string()} + {self.children[1].to_string()})"
        elif self.node_type == NodeType.SUB:
            return f"({self.children[0].to_string()} - {self.children[1].to_string()})"
        elif self.node_type == NodeType.MUL:
            return f"({self.children[0].to_string()} * {self.children[1].to_string()})"
        elif self.node_type == NodeType.DIV:
            return f"({self.children[0].to_string()} / {self.children[1].to_string()})"
        elif self.node_type == NodeType.POW:
            return f"({self.children[0].to_string()} ** {self.children[1].to_string()})"
        return "Unknown"


class ExpressionTree:
    """
    Complete mathematical expression tree representing a continuous candidate law:
        dx_i/dt = tree(x, u)
    """

    def __init__(self, root: ExpressionNode, variable_names: Optional[List[str]] = None):
        self.root = root
        self.variable_names = list(variable_names or [])

    def copy(self) -> "ExpressionTree":
        return ExpressionTree(self.root.copy(), list(self.variable_names))

    def evaluate(self, X: np.ndarray) -> np.ndarray:
        """
        Evaluate tree on state matrix X (M, n).
        """
        X = np.asarray(X, dtype=np.float64)
        if X.ndim == 1:
            X = X[:, np.newaxis]

        var_map = {}
        for idx, name in enumerate(self.variable_names):
            if idx < X.shape[1]:
                var_map[name] = X[:, idx]
            else:
                var_map[name] = np.zeros(X.shape[0], dtype=np.float64)

        return self.root.evaluate(var_map)

    def complexity(self) -> float:
        """
        Structural complexity score:
        C = node_count + 0.5 * max_depth + 0.2 * num_constants
        """
        nodes = self.root.count_nodes()
        depth = self.root.max_depth()
        constants = len(self.root.get_constants())
        return float(nodes + 0.5 * depth + 0.2 * constants)

    def count_nodes(self) -> int:
        return self.root.count_nodes()

    def max_depth(self) -> int:
        return self.root.max_depth()

    def get_constants(self) -> List[float]:
        return self.root.get_constants()

    def set_constants(self, values: List[float]):
        self.root.set_constants(values)

    def to_sympy(self) -> sp.Expr:
        return sp.simplify(self.root.to_sympy())

    def to_string(self) -> str:
        return self.root.to_string()

    def to_dict(self) -> Dict[str, Any]:
        def node_dict(node: ExpressionNode):
            return {
                "type": node.node_type.name,
                "name": node.name,
                "value": node.value,
                "children": [node_dict(c) for c in node.children],
                "units": node.units,
            }
        return {
            "variable_names": self.variable_names,
            "root": node_dict(self.root),
            "complexity": self.complexity(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpressionTree":
        def dict_to_node(d: Dict[str, Any]) -> ExpressionNode:
            return ExpressionNode(
                node_type=NodeType[d["type"]],
                name=d.get("name", ""),
                value=d.get("value", 0.0),
                children=[dict_to_node(c) for c in d.get("children", [])],
                units=d.get("units", {}),
            )
        return cls(dict_to_node(data["root"]), data.get("variable_names", []))

    @classmethod
    def from_sympy(cls, expr: sp.Expr, variable_names: List[str]) -> "ExpressionTree":
        """
        Convert arbitrary SymPy expression into an ExpressionTree AST.
        """
        def sympy_to_node(e: sp.Expr) -> ExpressionNode:
            if e.is_Symbol:
                return ExpressionNode(NodeType.VARIABLE, name=e.name)
            elif e.is_Number:
                return ExpressionNode(NodeType.CONSTANT, value=float(e))
            elif e.is_Add:
                # Binary reduction of additive arguments
                args = list(e.args)
                node = sympy_to_node(args[0])
                for arg in args[1:]:
                    node = ExpressionNode(NodeType.ADD, children=[node, sympy_to_node(arg)])
                return node
            elif e.is_Mul:
                args = list(e.args)
                node = sympy_to_node(args[0])
                for arg in args[1:]:
                    node = ExpressionNode(NodeType.MUL, children=[node, sympy_to_node(arg)])
                return node
            elif e.is_Pow:
                base, exp = e.args
                return ExpressionNode(NodeType.POW, children=[sympy_to_node(base), sympy_to_node(exp)])
            elif isinstance(e, sp.sin):
                return ExpressionNode(NodeType.SIN, children=[sympy_to_node(e.args[0])])
            elif isinstance(e, sp.cos):
                return ExpressionNode(NodeType.COS, children=[sympy_to_node(e.args[0])])
            elif isinstance(e, sp.exp):
                return ExpressionNode(NodeType.EXP, children=[sympy_to_node(e.args[0])])
            elif isinstance(e, sp.log):
                return ExpressionNode(NodeType.LOG, children=[sympy_to_node(e.args[0])])
            elif isinstance(e, sp.Abs):
                return ExpressionNode(NodeType.ABS, children=[sympy_to_node(e.args[0])])
            else:
                # Fallback constant approximation
                try:
                    return ExpressionNode(NodeType.CONSTANT, value=float(e.evalf()))
                except Exception:
                    return ExpressionNode(NodeType.CONSTANT, value=0.0)

        root = sympy_to_node(expr)
        return cls(root, variable_names)
