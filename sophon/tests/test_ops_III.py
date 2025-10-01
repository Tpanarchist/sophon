"""sophon.tests.test_ops_III

Unit tests for Book III operations in SOPHON.
Motif: Module (tests/test_ops_III)
Ports: [interface: Book III unit tests]
Invariants: [test coverage, correctness]
"""

from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType
from sophon.ops.euclid.book_III import REGISTRY

def test_bookIII_prop1_op():
    graph = HyperGraph()
    circle_id = graph.add_node(NodeType.CIRCLE, {"center": (0, 0), "radius": 1})
    op = REGISTRY.candidates("BookIII.Prop1")[0]
    assert op.precond(graph, circle_id)
    pt_id = op.apply(graph, circle_id)
    assert graph.nodes[pt_id].type == NodeType.POINT
    assert op.invariants(graph, pt_id)
