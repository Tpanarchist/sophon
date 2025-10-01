"""sophon.ops.registry

Defines the Op class and Registry for composable operations in SOPHON.
Motif: Module (ops/registry)
Ports: [interface: Op, Registry]
Invariants: [composability, extensibility]
"""

from typing import Any, Dict, List, Tuple, Optional
from sophon.core.hypergraph import HyperGraph

class Op:
    """Abstract base class for composable operations (Ops) in SOPHON."""
    name: str
    cost: float

    def precond(self, graph: HyperGraph) -> List[Tuple[Any, ...]]:
        """
        Enumerate all valid input tuples for this operation on the given graph.
        Returns a list of tuples, each representing a valid set of inputs.
        """
        raise NotImplementedError

    def apply(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> Any:
        """Apply the operation to the graph."""
        raise NotImplementedError

    def invariants(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> bool:
        """Check symbolic/numeric invariants after application."""
        raise NotImplementedError

class Registry:
    """Registry for available Ops."""
    def __init__(self):
        self._ops: Dict[str, Op] = {}

    def add(self, op: Op):
        self._ops[op.name] = op

    def candidates(self, name: Optional[str] = None, graph: Optional[HyperGraph] = None) -> List[Tuple[Op, Tuple[Any, ...]]]:
        """
        Enumerate all (op, valid_input_tuple) pairs for all registered ops.
        If name is provided, filter by op name.
        If graph is provided, use op.precond(graph) to enumerate valid inputs.
        """
        result: List[Tuple[Op, Tuple[Any, ...]]] = []
        ops = self._ops.values() if name is None else [op for op in self._ops.values() if op.name == name]
        if graph is not None:
            for op in ops:
                for input_tuple in op.precond(graph):
                    result.append((op, input_tuple))
            return result
        else:
            # If no graph is provided, just return ops with empty input tuple
            return [(op, ()) for op in ops]
