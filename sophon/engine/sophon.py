"""sophon.engine.sophon

Defines the main engine loop and orchestration logic for SOPHON.
Motif: Module (engine/sophon)
Ports: [interface: Engine, main loop]
Invariants: [system coherence, extensibility]
"""

import random
from typing import Any, List, Tuple
from sophon.affect.eoe import Valuator
from sophon.ops.registry import Registry, Op
from sophon.core.hypergraph import HyperGraph

class Engine:
    """Main SOPHON engine with Oak policy loop."""

    def __init__(
        self,
        graph: HyperGraph,
        registry: Registry,
        E: float = 10.0,
        m: float = 0.0,
        c2: float = 1.0
    ) -> None:
        self.graph = graph
        self.registry = registry
        self.valuator = Valuator(c2=c2)
        self.E = E  # Energy
        self.m = m  # Mass
        self.step_count = 0

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

        # 1. Get candidate operations and valid input tuples
        all_candidates = self.registry.candidates(graph=self.graph)
        if not all_candidates:
            return

        # Optionally subsample if too many candidates
        candidates = random.sample(all_candidates, min(max_candidates, len(all_candidates)))

        if not candidates:
            return

        # 2. Score candidates
        scored: List[Tuple[float, float, Op, Tuple[Any, ...], float]] = []
        for op, input_tuple in candidates:
            ep = self.predict(op, input_tuple)
            _, v, a = self.valuator.eoe(ep, P=1.0)  # Optimistic
            u = self.uncertainty(op, input_tuple)
            c = 0.0  # Closure (computed after apply)
            w = self.valuator.priority(v, a, u, c)
            scored.append((w, op.cost, op, input_tuple, ep))

        # 3. Select top-k within energy budget
        scored.sort(reverse=True, key=lambda x: x[0])
        chosen: List[Tuple[Op, Tuple[Any, ...], float]] = []
        budget = 0.0
        for w, cost, op, input_tuple, ep in scored:
            if budget + cost <= self.E:
                chosen.append((op, input_tuple, ep))
                budget += cost
            if len(chosen) >= k_commit:
                break

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

        self.step_count += 1
