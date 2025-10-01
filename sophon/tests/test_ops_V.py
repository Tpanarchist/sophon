"""sophon.tests.test_ops_V

Unit tests for Book V operations in SOPHON.
Motif: Module (tests/test_ops_V)
Ports: [interface: Book V unit tests]
Invariants: [test coverage, correctness]
"""

from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType
from sophon.ops.euclid.book_V import REGISTRY

def test_bookV_prop1_op():
    graph = HyperGraph()
    line1 = graph.add_node(NodeType.LINE, {"coords": ((0, 0), (1, 0))})
    line2 = graph.add_node(NodeType.LINE, {"coords": ((0, 0), (0, 1))})
    op = REGISTRY.candidates("BookV.Prop1")[0]
    assert op.precond(graph, line1, line2)
    result = op.apply(graph, line1, line2)
    assert result == (line1, line2)
    assert op.invariants(graph, line1, line2)
