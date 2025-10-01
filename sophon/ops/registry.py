"""sophon.ops.registry

Defines the Op class and Registry for composable operations in SOPHON.
Motif: Module (ops/registry)
Ports: [interface: Op, Registry]
Invariants: [composability, extensibility]
"""

from typing import Any, Dict, List, Optional
from sophon.core.hypergraph import HyperGraph

class Op:
    """Abstract base class for composable operations (Ops) in SOPHON."""
    name: str
    cost: float

    def precond(self, graph: HyperGraph, *args: Any, **kwargs: Any) -> bool:
        """Check if operation preconditions are satisfied."""
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

    def candidates(self, name: Optional[str] = None) -> List[Op]:
        if name is None:
            return list(self._ops.values())
        return [op for op in self._ops.values() if op.name == name]
