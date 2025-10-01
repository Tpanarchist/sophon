"""sophon.core.types

Defines enums and constants for node and edge types in the SOPHON typed hypergraph engine.
Motif: Module (core/types)
Ports: [interface: NodeType, EdgeType, constants]
Invariants: [type safety, extensibility]
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict, Tuple

class NodeType(Enum):
    POINT = auto()
    LINE = auto()
    CIRCLE = auto()
    POLYGON = auto()
    SOLID = auto()
    PERCEPT = auto()
    OPTION = auto()
    CONCEPT = auto()
    PROPOSITION = auto()
    PROOF = auto()
    SCHEMA = auto()
    EMOTION = auto()

class EdgeType(Enum):
    INCIDENCE = auto()
    CONSTRUCTION = auto()
    SUPPORTS = auto()
    CONTRADICTS = auto()
    DEFINES = auto()
    CAUSES = auto()
    TEMPORAL = auto()
    VALUATION = auto()
    PART_OF = auto()

@dataclass
class HNode:
    id: int
    type: NodeType
    attr: Dict[str, Any]

@dataclass
class HEdge:
    id: int
    type: EdgeType
    nodes: Tuple[int, ...]
    attr: Dict[str, Any]
