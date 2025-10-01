"""sophon.ops.integer_irrational

Provides helpers and operations for integer and irrational number concepts in SOPHON.
Motif: Module (ops/integer_irrational)
Ports: [interface: integer/irrational helpers, Op]
Invariants: [numeric correctness, composability]
"""

from typing import Any
from sophon.ops.registry import Op, Registry
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType, EdgeType

def is_integer(value: Any) -> bool:
    """Return True if value is an integer."""
    return isinstance(value, int)

def is_irrational(value: Any) -> bool:
    """Return True if value is a float and not rational (stub: always False for now)."""
    # Real implementation would check for irrationality
    return isinstance(value, float) and False

class IntegerConceptOp(Op):
    name = "IntegerConcept"
    cost = 1.0

    def precond(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> bool:
        # Expects a value as input
        if not args:
            return False
        return is_integer(args[0])

    def apply(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> Any:
        # Add a CONCEPT node for the integer value
        value = args[0]
        node_id = graph.add_node(NodeType.CONCEPT, {"value": value, "type": "integer"})
        return node_id

    def invariants(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> bool:
        node_id = args[0]
        node = graph.nodes.get(node_id)
        return node is not None and node.type == NodeType.CONCEPT and node.attr.get("type") == "integer"

REGISTRY = Registry()
REGISTRY.add(IntegerConceptOp())
