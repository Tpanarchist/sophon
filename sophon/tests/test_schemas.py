"""sophon.tests.test_schemas

Unit tests for schema miner in SOPHON.
Motif: Module (tests/test_schemas)
Ports: [interface: schema miner unit tests]
Invariants: [test coverage, correctness]
"""

from sophon.core.hypergraph import HyperGraph
from sophon.core.schemas import SchemaMiner, Schema

def test_schema_miner_empty():
    graph = HyperGraph()
    miner = SchemaMiner(graph)
    schemas = miner.mine_schemas()
    assert isinstance(schemas, list)
    assert all(isinstance(s, Schema) for s in schemas)
    assert schemas == []
