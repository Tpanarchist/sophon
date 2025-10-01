# SOPHON: Typed Hypergraph Cognitive Engine

## Overview

SOPHON is a modular, type-safe cognitive engine for geometric cognition, affective learning, and energy↔structure conversion. It encodes Euclid’s Elements as composable operations (Ops) on a typed hypergraph, supporting symbolic and numeric invariants, schema mining, and affective control.

## Architecture

- **Core:** Typed hypergraph (nodes, edges, schemas), types, registry
- **Ops:** Euclid Books I–XIII, primitives, integer/irrational, solids
- **Affect:** Equation of Emotion (EOE), energy↔mass tuning, closure gain
- **Engine:** Main orchestration logic
- **CLI:** Command-line interface for headless operation
- **Tests:** Pytest-based unit tests for all modules
- **Docs:** This file and implementation_plan.md

## Usage

1. Install Python 3.9+ and `pytest`.
2. Clone the repository and install dependencies if needed.
3. Run all tests and validation:
   ```
   python validate.py
   ```
4. Explore modules in `sophon/` for extensibility.

## Testing

- All modules are covered by unit tests in `sophon/tests/`.
- Run `python validate.py` to execute all tests and check invariants.

## Experiments

- See the `experiments/` directory for templates and long-run experiment scripts.
- To add a new experiment, copy `experiments/template_experiment.py` and follow the instructions in the file.

## References

- See `implementation_plan.md` for detailed requirements, architecture, and stepwise implementation.
- See code docstrings for motif, ports, and invariants.

---
Motif: Phase (docs), Ports: [overview, usage, experiments], Invariants: [documentation synchronization, mesh completeness]
