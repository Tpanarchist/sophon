"""sophon.ops.solids

Provides helpers and operations for solid (3D) geometric concepts in SOPHON.
Motif: Module (ops/solids)
Ports: [interface: solid helpers, Op]
Invariants: [geometric correctness, composability]
"""

from typing import Any
from sophon.ops.registry import Op, Registry
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType

def is_solid(value: Any) -> bool:
    """Return True if value is a dict with 'faces' and 'vertices' keys (stub for solid geometry)."""
    return isinstance(value, dict) and "faces" in value and "vertices" in value

class SolidConceptOp(Op):
    name = "SolidConcept"
    cost = 1.0

    def precond(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> bool:
        # Expects a value as input
        if not args:
            return False
        return is_solid(args[0])

    def apply(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> Any:
        # Add a SOLID node for the solid value
        value = args[0]
        node_id = graph.add_node(NodeType.SOLID, {"value": value, "type": "solid"})
        return node_id

    def invariants(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> bool:
        node_id = args[0]
        node = graph.nodes.get(node_id)
        return node is not None and node.type == NodeType.SOLID and node.attr.get("type") == "solid"

REGISTRY = Registry()
REGISTRY.add(SolidConceptOp())
