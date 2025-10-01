"""sophon.core.hypergraph

Implements the core hypergraph data structures and operations for SOPHON.
Motif: Module (core/hypergraph)
Ports: [interface: HyperGraph, HNode, HEdge]
Invariants: [type safety, compositionality]
"""

from typing import Any, Dict, Optional, Set, Tuple
from .types import HNode, HEdge, NodeType, EdgeType

class HyperGraph:
    def __init__(self):
        self.nodes: Dict[int, HNode] = {}
        self.edges: Dict[int, HEdge] = {}
        self._next_node_id = 1
        self._next_edge_id = 1

    def add_node(self, type: NodeType, attr: Optional[Dict[str, Any]] = None) -> int:
        node_id = self._next_node_id
        self.nodes[node_id] = HNode(id=node_id, type=type, attr=attr or {})
        self._next_node_id += 1
        return node_id

    def add_edge(self, type: EdgeType, nodes: Tuple[int, ...], attr: Optional[Dict[str, Any]] = None) -> int:
        edge_id = self._next_edge_id
        self.edges[edge_id] = HEdge(id=edge_id, type=type, nodes=nodes, attr=attr or {})
        self._next_edge_id += 1
        return edge_id

    def neighbors(self, node_id: int) -> Set[int]:
        nbrs: Set[int] = set()
        for edge in self.edges.values():
            if node_id in edge.nodes:
                nbrs.update(edge.nodes)
        nbrs.discard(node_id)
        return nbrs

    def by_type(self, node_type: Optional[NodeType] = None, edge_type: Optional[EdgeType] = None):
        nodes = [n for n in self.nodes.values() if node_type is None or n.type == node_type]
        edges = [e for e in self.edges.values() if edge_type is None or e.type == edge_type]
        return nodes, edges
