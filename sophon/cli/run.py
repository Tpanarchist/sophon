"""sophon.cli.run

Provides the CLI entry point for running the SOPHON engine.
Motif: Module (cli/run)
Ports: [interface: CLI runner]
Invariants: [usability, headless operation]
"""

import argparse
import logging
import os
from typing import Optional, Any, List, Tuple, Dict, cast
from sophon.core.hypergraph import HyperGraph
from sophon.ops.registry import Registry
from sophon.engine.sophon import Engine

# Import all available book registries
from sophon.ops.euclid.book_I import REGISTRY as BOOK_I_REGISTRY
from sophon.ops.euclid.book_II import REGISTRY as BOOK_II_REGISTRY

def configure_logging(args: argparse.Namespace) -> None:
    level: int
    log_level_env = os.getenv("SOPHON_LOG_LEVEL")
    log_level_arg: Optional[str] = getattr(args, "log_level", None)
    if log_level_arg:
        level = getattr(logging, log_level_arg.upper(), logging.INFO)
    elif getattr(args, "debug", False):
        level = logging.DEBUG
    elif getattr(args, "verbose", False):
        level = logging.INFO
    elif getattr(args, "quiet", False):
        level = logging.ERROR
    else:
        level = getattr(logging, (log_level_env or "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")

def main():
    parser = argparse.ArgumentParser(description='Run SOPHON engine')
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--report-every', type=int, default=100)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--verbose', action='store_true', help='Enable INFO-level output')
    parser.add_argument('--debug', action='store_true', help='Enable DEBUG-level output')
    parser.add_argument('--quiet', action='store_true', help='Only show errors')
    parser.add_argument('--log-level', type=str, choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], help='Override log level')
    parser.add_argument('--min-energy-floor', type=float, default=1.0, help='Minimum selection budget floor')
    parser.add_argument('--no-greedy-fallback', action='store_true', help='Disable greedy fallback when no ops are chosen')
    args = parser.parse_args()
    configure_logging(args)
    logger = logging.getLogger("sophon.cli")

    if args.seed is not None:
        import random
        random.seed(args.seed)

    # Setup
    graph = HyperGraph()
    registry = Registry()

    # Load ops from multiple books
    for op in BOOK_I_REGISTRY.ops():
        registry.add(op)
    for op in BOOK_II_REGISTRY.ops():
        registry.add(op)

    # Initialize engine with enhanced exploration
    verbosity = 1 if args.debug else 0
    engine = Engine(
        graph,
        registry,
        E=15.0,  # More energy for multiple operations
        m=0.0,
        verbosity=verbosity,
        min_energy_floor=args.min_energy_floor,
        force_greedy_if_empty=(not args.no_greedy_fallback),
        epsilon=0.3,  # 30% exploration rate
        top_n_explore=15,  # Explore from top 15 candidates
        recent_window=10  # Larger diversity tracking window
    )
    engine.seed_graph(num_points=5, num_lines=3)

    logger.info(f"Starting SOPHON with {len(registry.ops())} ops")

    # Run
    for step in range(args.steps):
        engine.step()
        if (step + 1) % args.report_every == 0:
            logger.info(f"Step {step + 1}:")
            logger.info(f"  Nodes: {len(graph.nodes)}")
            logger.info(f"  Edges: {len(graph.edges)}")
            logger.info(f"  Energy: {engine.E:.2f}")
            logger.info(f"  Mass: {engine.m:.2f}")
            summary: Dict[str, Any] = engine.get_last_summary() or {}
            candidates = int(summary.get("candidates", 0))
            chosen = int(summary.get("chosen", 0))
            top_op = summary.get("top_op")
            top_score = summary.get("top_score")
            rewards = cast(List[float], summary.get("rewards", []))
            topk = cast(List[Tuple[str, float]], summary.get("topk", []))
            chosen_ops = cast(List[Tuple[str, Tuple[Any, ...]]], summary.get("chosen_ops", []))
            budget = float(summary.get("budget_spent", 0.0))
            available = float(summary.get("available_budget", 0.0))
            fallback_used = bool(summary.get("fallback_used", False))
            avg_r = (sum(rewards) / len(rewards)) if rewards else 0.0
            max_r = max(rewards) if rewards else 0.0
            logger.info(f"  Candidates: {candidates} | Chosen: {chosen} | Top: {top_op or '-'}{f' {top_score:.3f}' if top_score is not None else ''}")
            if topk:
                logger.info("  TopK: " + ", ".join(f"{name}:{score:.3f}" for name, score in topk))
            if chosen_ops:
                shown = ", ".join(f"{name}{inputs}" for name, inputs in chosen_ops[:2])
                more = f" (+{len(chosen_ops)-2} more)" if len(chosen_ops) > 2 else ""
                logger.info(f"  Applied: {shown}{more} | Budget: {budget:.2f}/{available:.2f} | Fallback: {fallback_used}")
            logger.info(f"  Rewards: n={len(rewards)} avg={avg_r:.3f} max={max_r:.3f}")

    logger.info("Run complete.")

if __name__ == '__main__':
    main()
