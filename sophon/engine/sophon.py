"""sophon.engine.sophon

Defines the main engine loop and orchestration logic for SOPHON.
Motif: Module (engine/sophon)
Ports: [interface: Engine, main loop]
Invariants: [system coherence, extensibility]
"""

import logging, random
from typing import Any, List, Tuple, Dict, Optional
from sophon.affect.eoe import Valuator
from sophon.ops.registry import Registry, Op
from sophon.core.hypergraph import HyperGraph
from sophon.core.types import NodeType

class Engine:
    """Main SOPHON engine with Oak policy loop."""

    def __init__(
        self,
        graph: HyperGraph,
        registry: Registry,
        E: float = 10.0,
        m: float = 0.0,
        c2: float = 1.0,
        verbosity: int = 0
    ) -> None:
        self.graph = graph
        self.registry = registry
        self.valuator = Valuator(c2=c2)
        self.E = E  # Energy
        self.m = m  # Mass
        self.step_count = 0
        self.verbosity = verbosity
        self.logger = logging.getLogger("sophon.engine")
        self._last_summary: Dict[str, Any] = {}

    def predict(self, op: Op, inputs: Tuple[Any, ...]) -> float:
        """Predict outcome (ep). Simple heuristic for now."""
        return 0.5  # Optimistic baseline

    def uncertainty(self, op: Op, inputs: Tuple[Any, ...]) -> float:
        """Estimate uncertainty/novelty."""
        return random.random()

    def closure_gain(self, outputs: Any) -> float:
        """Estimate how much this closes loops/proofs."""
        if outputs and "prop" in str(outputs):
            return 0.5
        return 0.0

    def step(
        self,
        max_candidates: int = 64,
        k_commit: int = 4,
        release_prob: float = 0.1
    ) -> None:
        """Execute one Oak policy step."""

        # 1. Enumerate all valid (op, inputs) pairs
        candidates: List[Tuple[Op, Tuple[Any, ...]]] = []
        ops_list = self.registry.ops()
        if self.logger.isEnabledFor(logging.DEBUG):
            names = [op.name for op in ops_list]
            self.logger.debug(f"Checking {len(ops_list)} ops for valid inputs...")
            self.logger.debug(f"ops_list = {names}")
        for op in ops_list:
            try:
                valid_inputs = op.precond(self.graph)
                for inputs in valid_inputs:
                    candidates.append((op, inputs))
                    if len(candidates) >= max_candidates:
                        break
            except Exception:
                pass
            if len(candidates) >= max_candidates:
                break

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Found {len(candidates)} valid (op, inputs) pairs")
        if not candidates:
            return

        # 2. Score candidates
        scored: List[Tuple[float, float, Op, Tuple[Any, ...], float]] = []
        for op, inputs in candidates:
            ep = self.predict(op, inputs)
            _, v, a = self.valuator.eoe(ep, P=1.0)  # Optimistic
            u = self.uncertainty(op, inputs)
            c = 0.0  # Closure (computed after apply)
            w = self.valuator.priority(v, a, u, c)
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"SCORE op={op.name} inputs={inputs} score={w:.3f} cost={op.cost} energy={self.E:.3f}")
            scored.append((w, op.cost, op, inputs, ep))

        # 3. Select top-k within energy budget
        scored.sort(reverse=True, key=lambda x: x[0])
        top_op_name: Optional[str] = None
        top_score: Optional[float] = None
        top_inputs: Optional[Tuple[Any, ...]] = None
        topk: List[Tuple[str, float]] = []
        if scored:
            top_score = scored[0][0]
            top_op_name = scored[0][2].name
            top_inputs = scored[0][3]
            topk = [(s[2].name, s[0]) for s in scored[:3]]
        chosen: List[Tuple[Op, Tuple[Any, ...], float]] = []
        budget = 0.0
        for w, cost, op, input_tuple, ep in scored:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"CHOOSE w={w:.3f} cost={cost} budget={budget:.3f} E={self.E:.3f}")
            if budget + cost <= self.E:
                chosen.append((op, input_tuple, ep))
                budget += cost
            if len(chosen) >= k_commit:
                break

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Chose {len(chosen)} ops to apply")

        # 4. Apply chosen ops and compute actual rewards
        rewards: List[float] = []
        for op, input_tuple, ep in chosen:
            try:
                outputs = op.apply(self.graph, *input_tuple)
                ok = op.invariants(self.graph, outputs) if outputs else False
                p = 1.0 if ok else 0.0

                _, v, a = self.valuator.eoe(ep, p)
                c = self.closure_gain(outputs)
                r = max(0.0, 0.6 * v + 0.4 * a + c)
                rewards.append(r)
            except Exception:
                rewards.append(0.0)

        # 5. Consolidate (e → m)
        self.E, self.m = self.valuator.consolidate(self.E, self.m, rewards)

        # 6. Occasionally release (m → e)
        if random.random() < release_prob:
            self.E, self.m = self.valuator.release(self.E, self.m, dm=0.1)

        # Save summary for external reporting
        chosen_ops = [(op.name, input_tuple) for (op, input_tuple, _ep) in chosen]
        self._last_summary = {
            "step": self.step_count + 1,
            "ops_count": len(ops_list),
            "candidates": len(candidates),
            "chosen": len(chosen),
            "chosen_ops": chosen_ops,
            "budget_spent": budget,
            "top_op": top_op_name,
            "top_score": top_score,
            "top_inputs": top_inputs,
            "topk": topk,
            "rewards": rewards,
            "energy": self.E,
            "mass": self.m,
        }
        self.step_count += 1

    def get_last_summary(self) -> Dict[str, Any]:
        """Return last step summary for reporting."""
        return self._last_summary

    def seed_graph(self, num_points: int = 3, num_lines: int = 2) -> None:
        """Create initial geometric objects to bootstrap."""
        import random

        # Create some random points
        points = []
        for i in range(num_points):
            x = random.uniform(-5, 5)
            y = random.uniform(-5, 5)
            pid = self.graph.add_node(NodeType.POINT, {'x': x, 'y': y, 'name': f'P{i}'})
            points.append(pid)

        # Create some lines connecting points
        for i in range(num_lines):
            if len(points) >= 2:
                p1 = random.choice(points)
                p2 = random.choice([p for p in points if p != p1])
                self.graph.add_node(NodeType.LINE, {'p1': p1, 'p2': p2})

        self.logger.info(f"Seeded graph with {num_points} points and {num_lines} lines")
        # Debug: print all POINT and LINE nodes after seeding
        if self.logger.isEnabledFor(logging.DEBUG):
            for node_id, node in self.graph.nodes.items():
                if node.type == NodeType.POINT or node.type == NodeType.LINE:
                    self.logger.debug(f"NODE {node_id}: type={node.type} attr={node.attr}")
