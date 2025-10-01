"""sophon.tests.test_ops_IV

Unit tests for Book IV operations in SOPHON.
Motif: Module (tests/test_ops_IV)
Ports: [interface: Book IV unit tests]
Invariants: [test coverage, correctness]
"""

from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType
from sophon.ops.euclid.book_IV import REGISTRY

def test_bookIV_prop1_op():
    graph = HyperGraph()
    poly_id = graph.add_node(NodeType.POLYGON, {"sides": 5})
    op = REGISTRY.candidates("BookIV.Prop1")[0]
    assert op.precond(graph, poly_id)
    circ_id = op.apply(graph, poly_id)
    assert graph.nodes[circ_id].type == NodeType.CIRCLE
    assert op.invariants(graph, circ_id)
