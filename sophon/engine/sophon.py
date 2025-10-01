"""sophon.engine.sophon

Defines the main engine loop and orchestration logic for SOPHON.
Motif: Module (engine/sophon)
Ports: [interface: Engine, main loop]
Invariants: [system coherence, extensibility]
"""

import logging, random
from collections import deque
from typing import Any, List, Tuple, Dict, Optional, Set, Deque
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
        verbosity: int = 0,
        min_energy_floor: float = 1.0,
        force_greedy_if_empty: bool = True,
        epsilon: float = 0.2,
        top_n_explore: int = 10,
        recent_window: int = 5
    ) -> None:
        self.graph = graph
        self.registry = registry
        self.valuator = Valuator(c2=c2)
        self.E = E  # Energy
        self.m = m  # Mass
        self.step_count = 0
        self.verbosity = verbosity
        self.logger = logging.getLogger("sophon.engine")
        self.min_energy_floor = min_energy_floor
        self.force_greedy_if_empty = force_greedy_if_empty
        self.epsilon = epsilon
        self.top_n_explore = top_n_explore
        self.recent_ops: Deque[str] = deque(maxlen=recent_window)
        self.op_counts: Dict[str, int] = {}
        self.seen_applications: Set[Tuple[str, Tuple[Any, ...]]] = set()
        self.seen_props: Set[int] = set()
        self.unique_props_total: int = 0
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
        available_budget = max(self.E, self.min_energy_floor)
        budget = 0.0
        fallback_used = False
        explore_used = False
        picked_key: Optional[Tuple[str, Tuple[Any, ...]]] = None
        # Epsilon-greedy selection for the first pick from top-N
        if self.epsilon > 0.0 and random.random() < self.epsilon and scored:
            eligible_top = [item for item in scored[:self.top_n_explore] if item[1] <= available_budget]
            if eligible_top:
                w_sel, cost_sel, op_sel, inputs_sel, ep_sel = random.choice(eligible_top)
                chosen.append((op_sel, inputs_sel, ep_sel))
                budget += cost_sel
                explore_used = True
                picked_key = (op_sel.name, inputs_sel)
        for w, cost, op, input_tuple, ep in scored:
            if picked_key is not None and op.name == picked_key[0] and input_tuple == picked_key[1]:
                picked_key = None
                continue
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"CHOOSE w={w:.3f} cost={cost} budget={budget:.3f} E={self.E:.3f}")
            if budget + cost <= available_budget:
                chosen.append((op, input_tuple, ep))
                budget += cost
            if len(chosen) >= k_commit:
                break

        if not chosen and scored and self.force_greedy_if_empty:
            best_w, best_cost, best_op, best_inputs, best_ep = scored[0]
            self.logger.info(
                "Greedy fallback: applying %s score=%.3f with E=%.3f cost=%.3f",
                best_op.name, best_w, self.E, best_cost
            )
            chosen.append((best_op, best_inputs, best_ep))
            budget += best_cost
            fallback_used = True

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Chose {len(chosen)} ops to apply")

        # 4. Apply chosen ops and compute actual rewards
        rewards: List[float] = []
        novelty_nodes_step = 0
        novelty_edges_step = 0
        for op, input_tuple, ep in chosen:
            try:
                pre_node_ids = set(self.graph.nodes.keys())
                pre_nodes_len = len(self.graph.nodes)
                pre_edges_len = len(self.graph.edges)

                outputs = op.apply(self.graph, *input_tuple)
                ok = op.invariants(self.graph, outputs) if outputs else False
                p = 1.0 if ok else 0.0

                _, v, a = self.valuator.eoe(ep, p)
                c = self.closure_gain(outputs)
                base = max(0.0, 0.6 * v + 0.4 * a + c)

                post_nodes_len = len(self.graph.nodes)
                post_edges_len = len(self.graph.edges)
                delta_nodes = max(0, post_nodes_len - pre_nodes_len)
                delta_edges = max(0, post_edges_len - pre_edges_len)
                novelty_nodes_step += delta_nodes
                novelty_edges_step += delta_edges

                # Enhanced reward calculation with more diversity incentives
                new_prop_bonus = 0.0
                new_ids = set(self.graph.nodes.keys()) - pre_node_ids
                for nid in new_ids:
                    node = self.graph.nodes.get(nid)
                    if node and getattr(node, "type", None) == NodeType.PROPOSITION and nid not in self.seen_props:
                        self.seen_props.add(nid)
                        self.unique_props_total += 1
                        new_prop_bonus += 0.3

                # Strong diversity bonus for using different operations
                diversity_bonus = 0.0
                if len(self.recent_ops) > 0:
                    if self.recent_ops[-1] != op.name:
                        diversity_bonus += 0.25  # Significant bonus for operation diversity
                    if len(self.recent_ops) >= 3 and op.name not in list(self.recent_ops)[-3:]:
                        diversity_bonus += 0.15  # Extra bonus for novel operations

                # Unique application bonus (never tried this exact input before)
                unique_apply_bonus = 0.2 if (op.name, input_tuple) not in self.seen_applications else 0.0
                if unique_apply_bonus > 0:
                    self.seen_applications.add((op.name, input_tuple))

                # Progressive repeat penalty (gets worse with more repetitions)
                repeat_count = self.op_counts.get(op.name, 0)
                repeat_penalty = min(repeat_count * 0.15, 0.8)  # More severe penalty

                # Complexity bonus for more sophisticated operations
                complexity_bonus = 0.0
                if "II" in op.name or "III" in op.name:  # Higher book operations
                    complexity_bonus += 0.2
                if outputs and isinstance(outputs, dict):
                    if 'square' in outputs or 'rectangle' in outputs:
                        complexity_bonus += 0.15
                    if 'new_points' in outputs and len(outputs.get('new_points', [])) > 1:
                        complexity_bonus += 0.1

                # Novel structure bonus
                structure_bonus = 0.0
                if delta_nodes >= 2:  # Created multiple new nodes
                    structure_bonus += 0.1
                if delta_edges >= 1:  # Created new connections
                    structure_bonus += 0.05

                r = max(0.0, base + 0.02 * delta_nodes + 0.02 * delta_edges + 
                       new_prop_bonus + diversity_bonus + unique_apply_bonus + 
                       complexity_bonus + structure_bonus - repeat_penalty)
                rewards.append(r)

                # Update op history
                self.op_counts[op.name] = self.op_counts.get(op.name, 0) + 1
                self.recent_ops.append(op.name)
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
            "available_budget": available_budget,
            "fallback_used": fallback_used,
            "explore_used": explore_used,
            "top_op": top_op_name,
            "top_score": top_score,
            "top_inputs": top_inputs,
            "topk": topk,
            "rewards": rewards,
            "novelty_nodes_step": novelty_nodes_step,
            "novelty_edges_step": novelty_edges_step,
            "unique_props_total": self.unique_props_total,
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
