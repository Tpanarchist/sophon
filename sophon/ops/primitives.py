"""sophon.ops.primitives

Provides geometric helper functions and primitives for SOPHON.
Motif: Module (ops/primitives)
Ports: [interface: geometric helpers]
Invariants: [reusability, geometric correctness]
"""

from typing import Tuple

def midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
    """Return the midpoint between two points."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def perpendicular_bisector(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Return the midpoint and a direction vector for the perpendicular bisector of segment p1-p2."""
    mid = midpoint(p1, p2)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    perp_dir = (-dy, dx)
    return mid, perp_dir

def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Return the Euclidean distance between two points."""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
