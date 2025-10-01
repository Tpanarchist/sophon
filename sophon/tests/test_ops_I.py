"""sophon.tests.test_ops_I

Unit tests for Book I operations and primitives in SOPHON.
Motif: Module (tests/test_ops_I)
Ports: [interface: Book I unit tests]
Invariants: [test coverage, correctness]
"""

import pytest
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType
from sophon.ops.euclid.book_I import REGISTRY
from sophon.ops.primitives import midpoint, perpendicular_bisector, distance

def test_midpoint():
    assert midpoint((0, 0), (2, 2)) == (1, 1)
    assert midpoint((1, 5), (3, 1)) == (2, 3)

def test_perpendicular_bisector():
    mid, perp = perpendicular_bisector((0, 0), (2, 0))
    assert mid == (1, 0)
    assert perp == (0, 2)

def test_distance():
    assert distance((0, 0), (3, 4)) == 5.0
    assert distance((1, 1), (4, 5)) == 5.0

def test_bookI_prop1_op():
    graph = HyperGraph()
    line_id = graph.add_node(NodeType.LINE, {"coords": ((0, 0), (1, 0))})
    op = REGISTRY.candidates("BookI.Prop1")[0]
    assert op.precond(graph, line_id)
    tri_id = op.apply(graph, line_id)
    assert graph.nodes[tri_id].type == NodeType.POLYGON
    assert graph.nodes[tri_id].attr["sides"] == 3
    assert op.invariants(graph, tri_id)
