"""sophon.tests.test_ops_VI

Unit tests for Book VI operations in SOPHON.
Motif: Module (tests/test_ops_VI)
Ports: [interface: Book VI unit tests]
Invariants: [test coverage, correctness]
"""

from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType
from sophon.ops.euclid.book_VI import REGISTRY

def test_bookVI_prop1_op():
    graph = HyperGraph()
    poly1 = graph.add_node(NodeType.POLYGON, {"sides": 3})
    poly2 = graph.add_node(NodeType.POLYGON, {"sides": 3})
    op = REGISTRY.candidates("BookVI.Prop1")[0]
    assert op.precond(graph, poly1, poly2)
    result = op.apply(graph, poly1, poly2)
    assert result == (poly1, poly2)
    assert op.invariants(graph, poly1, poly2)
