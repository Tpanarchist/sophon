# Implementation Plan

[Overview]
Design and implement SOPHON, a modular typed-hypergraph cognitive engine for geometric cognition, affective learning, and energy↔structure conversion, as specified in the provided contract.

SOPHON is a Python-based engine that encodes Euclid’s Elements (Books I–XIII) as composable operations on a typed hypergraph, guided by an affective controller (Equation of Emotion) and energy↔mass consolidation dynamics. The system is modular, DRY, CLI-friendly, and headless, with pluggable storage and a focus on symbolic and numeric invariants. The implementation will follow a phased approach, starting with the core skeleton, then incrementally adding Euclid content, learning mechanisms, and validation utilities.

[Types]
The type system will be extended to include enums for node and edge types, and data structures for hypergraph nodes, edges, and schemas.

- NodeType (Enum): POINT, LINE, CIRCLE, POLYGON, SOLID, PERCEPT, OPTION, CONCEPT, PROPOSITION, PROOF, SCHEMA, EMOTION
- EdgeType (Enum): INCIDENCE, CONSTRUCTION, SUPPORTS, CONTRADICTS, DEFINES, CAUSES, TEMPORAL, VALUATION, PART_OF
- HNode: id (int), type (NodeType), attr (dict)
- HEdge: id (int), type (EdgeType), nodes (tuple[int,...]), attr (dict)
- HyperGraph: add_node, add_edge, neighbors, by_type
- Op: name, cost, precond, apply, invariants
- Registry: add, candidates
- Valuator: eoe, priority, consolidate, release

[Files]
The implementation will create new files and directories as specified, with no deletions or moves required.

- New files:
  - sophon/core/types.py: enums & constants
  - sophon/core/hypergraph.py: hypergraph data structures
  - sophon/core/storage.py: JSONL/SQLite serializers
  - sophon/core/selectors.py: graph queries
  - sophon/core/schemas.py: schema representation & mining
  - sophon/affect/eoe.py: EoE, priority, energy↔mass
  - sophon/affect/traces.py: valuation event logs
  - sophon/ops/registry.py: Op class, Registry
  - sophon/ops/primitives.py: geometric helpers
  - sophon/ops/euclid/book_I.py ... book_XIII.py: Euclid content
  - sophon/ops/compile.py: load/register all books
  - sophon/engine/sophon.py: main loop
  - sophon/engine/metrics.py: reporting utilities
  - sophon/engine/validator.py: invariant checks
  - sophon/cli/run.py: CLI runner
  - sophon/cli/inspect.py: state inspection
  - sophon/cli/export.py: export utilities
  - sophon/tests/test_core.py, test_affect.py, test_ops_I.py ... test_ops_XIII.py, test_engine.py
  - docs/00_overview.md ... docs/07_extending.md
  - pyproject.toml, README.md, LICENSE

- Existing files to modify: None (empty repo)
- Files to delete/move: None
- Configuration updates: pyproject.toml for Python ≥3.11, optional extras

[Functions]
The implementation will introduce new functions for all core operations, with no removals.

- New functions:
  - HyperGraph: add_node, add_edge, neighbors, by_type
  - Op: precond, apply, invariants
  - Registry: add, candidates
  - Valuator: eoe, priority, consolidate, release
  - CLI: run, inspect, export
  - Book Ops: precond, apply, invariants for each proposition
  - Primitives: geometric helpers (midpoint, perpendicular, etc.)
  - Validator: numeric/symbolic checks
  - Metrics: reporting utilities

- Modified functions: None (new codebase)
- Removed functions: None

[Classes]
The implementation will introduce new classes for all core abstractions, with no removals.

- New classes:
  - NodeType, EdgeType (Enum)
  - HNode, HEdge, HyperGraph
  - Op, Registry
  - Valuator
  - Engine
  - Book-specific Op subclasses
  - Schema miner, Validator, Metrics

- Modified classes: None
- Removed classes: None

[Dependencies]
The implementation will add Python ≥3.11 as a requirement, with no external dependencies required by default.

- New: Python ≥3.11 (pyproject.toml)
- Optional: JSONL, SQLite (standard library or optional extras)
- No third-party packages required for core functionality

[Testing]
The implementation will use unit tests for all core modules and each Euclid proposition, plus integration tests for the engine and persistence.

- New test files: tests/test_core.py, test_affect.py, test_ops_I.py ... test_ops_XIII.py, test_engine.py
- Test requirements: pytest or unittest (optional, can use stdlib)
- Validation: Each Op must have at least one checkable invariant; engine and schema mining must be validated with synthetic and long-run tests

[Implementation Order]
The implementation will proceed in a phased, dependency-ordered sequence.

1. Phase 0: Implement core/types.py, core/hypergraph.py, ops/registry.py, affect/eoe.py, engine/sophon.py (skeleton), cli/run.py
2. Phase 1: Implement all Book I Ops, primitives, and unit tests
3. Phase 2: Implement Books II–VI, schema miner, and tests
4. Phase 3: Implement Books VII–X, integer/irrational concepts, and tests
5. Phase 4: Implement Books XI–XIII, solids, and tests
6. Phase 5: Implement learning polish, energy↔mass tuning, closure gain, and release policy
7. Phase 6: Implement validation, docs, and long-run experiments
