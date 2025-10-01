"""sophon.ops.euclid.book_I

Implements Book I operations (propositions, constructions, proofs) from Euclid's Elements for SOPHON.
Motif: Module (ops/euclid/book_I)
Ports: [interface: Book I Ops, Propositions, Proofs]
Invariants: [axiomatic correctness, composability]
"""

from typing import Any
from sophon.ops.registry import Op, Registry
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType, EdgeType

class BookIProp1Op(Op):
    name = "BookI.Prop1"
    cost = 1.0

    def precond(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> bool:
        # Example: expects a single LINE node id as input
        if not args or not isinstance(args[0], int):
            return False
        node_id = args[0]
        node = graph.nodes.get(node_id)
        return node is not None and node.type == NodeType.LINE

    def apply(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> Any:
        # Example: construct an equilateral triangle on a given line
        node_id = args[0]
        # In a real implementation, geometric construction would occur here
        # For now, just add a POLYGON node and connect it to the line
        tri_id = graph.add_node(NodeType.POLYGON, {"sides": 3, "constructed_by": self.name})
        graph.add_edge(EdgeType.CONSTRUCTION, (node_id, tri_id), {"desc": "equilateral triangle"})
        return tri_id

    def invariants(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> bool:
        # Example: check that the constructed polygon has 3 sides
        tri_id = args[0]
        node = graph.nodes.get(tri_id)
        return node is not None and node.type == NodeType.POLYGON and node.attr.get("sides") == 3

REGISTRY = Registry()
REGISTRY.add(BookIProp1Op())
