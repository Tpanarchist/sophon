"""sophon.tests.test_ops_II

Unit tests for Book II operations in SOPHON.
Motif: Module (tests/test_ops_II)
Ports: [interface: Book II unit tests]
Invariants: [test coverage, correctness]
"""

from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType
from sophon.ops.euclid.book_II import REGISTRY

def test_bookII_prop1_op():
    graph = HyperGraph()
    line_id = graph.add_node(NodeType.LINE, {"coords": ((0, 0), (1, 0))})
    op = REGISTRY.candidates("BookII.Prop1")[0]
    assert op.precond(graph, line_id)
    para_id = op.apply(graph, line_id)
    assert graph.nodes[para_id].type == NodeType.POLYGON
    assert graph.nodes[para_id].attr["sides"] == 4
    assert op.invariants(graph, para_id)
