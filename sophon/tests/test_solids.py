"""sophon.tests.test_solids

Unit tests for solid (3D) logic in SOPHON.
Motif: Module (tests/test_solids)
Ports: [interface: solid unit tests]
Invariants: [test coverage, correctness]
"""

from sophon.ops.solids import is_solid, REGISTRY
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType

def test_is_solid():
    assert is_solid({"faces": 6, "vertices": 8})
    assert not is_solid({"faces": 6})
    assert not is_solid(42)

def test_solid_concept_op():
    graph = HyperGraph()
    op = REGISTRY.candidates("SolidConcept")[0]
    solid_val = {"faces": 6, "vertices": 8}
    assert op.precond(graph, solid_val)
    node_id = op.apply(graph, solid_val)
    node = graph.nodes[node_id]
    assert node.type == NodeType.SOLID
    assert node.attr["type"] == "solid"
    assert node.attr["value"] == solid_val
    assert op.invariants(graph, node_id)
