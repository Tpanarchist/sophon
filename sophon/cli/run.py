"""sophon.cli.run

Provides the CLI entry point for running the SOPHON engine.
Motif: Module (cli/run)
Ports: [interface: CLI runner]
Invariants: [usability, headless operation]
"""

import argparse
from sophon.core.hypergraph import HyperGraph
from sophon.ops.registry import Registry
from sophon.engine.sophon import Engine

# Import Book I registry
from sophon.ops.euclid.book_I import REGISTRY as BOOK_I_REGISTRY

def main():
    parser = argparse.ArgumentParser(description='Run SOPHON engine')
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--report-every', type=int, default=100)
    parser.add_argument('--seed', type=int, default=None)
    args = parser.parse_args()

    if args.seed is not None:
        import random
        random.seed(args.seed)

    # Setup
    graph = HyperGraph()
    registry = Registry()

    # Load all Book I ops
    for op in BOOK_I_REGISTRY._ops.values():
        registry.add(op)

    # Initialize engine
    engine = Engine(graph, registry, E=10.0, m=0.0)

    print(f"Starting SOPHON with {len(registry._ops)} ops")

    # Run
    for step in range(args.steps):
        engine.step()
        if (step + 1) % args.report_every == 0:
            print(f"Step {step + 1}:")
            print(f"  Nodes: {len(graph.nodes)}")
            print(f"  Edges: {len(graph.edges)}")
            print(f"  Energy: {engine.E:.2f}")
            print(f"  Mass: {engine.m:.2f}")

    print("\nRun complete.")

if __name__ == '__main__':
    main()
