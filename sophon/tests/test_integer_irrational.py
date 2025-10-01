"""sophon.tests.test_integer_irrational

Unit tests for integer and irrational logic in SOPHON.
Motif: Module (tests/test_integer_irrational)
Ports: [interface: integer/irrational unit tests]
Invariants: [test coverage, correctness]
"""

from sophon.ops.integer_irrational import is_integer, is_irrational, REGISTRY
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType

def test_is_integer():
    assert is_integer(5)
    assert not is_integer(5.0)
    assert not is_integer("5")

def test_is_irrational():
    assert not is_irrational(5)
    assert not is_irrational(5.0)
    assert not is_irrational("sqrt(2)")

def test_integer_concept_op():
    graph = HyperGraph()
    op = REGISTRY.candidates("IntegerConcept")[0]
    assert op.precond(graph, 7)
    node_id = op.apply(graph, 7)
    node = graph.nodes[node_id]
    assert node.type == NodeType.CONCEPT
    assert node.attr["type"] == "integer"
    assert node.attr["value"] == 7
    assert op.invariants(graph, node_id)
